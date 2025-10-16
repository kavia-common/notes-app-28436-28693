from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_preview_or_current_user
from app.db.session import get_session
from app.models.note import Note
from app.models.summary import Summary
from app.schemas.note import NoteCreate, NoteUpdate, NoteRead
from app.schemas.summary import SummaryRead
from app.services.summarization_client import SummarizationClient

router = APIRouter()


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[NoteRead],
    summary="List notes",
    description="List notes for the authenticated user.",
)
async def list_notes(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_preview_or_current_user),
) -> List[NoteRead]:
    """
    List notes for current user.

    Args:
        session: Async database session.
        user: Current authenticated user.

    Returns:
        List[NoteRead]: Notes owned by the user.
    """
    result = await session.execute(select(Note).where(Note.user_id == user.id).order_by(Note.created_at.desc()))
    notes = result.scalars().all()
    return [NoteRead.model_validate(n) for n in notes]


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
    description="Create a new note for the current user.",
)
async def create_note(
    payload: NoteCreate,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_preview_or_current_user),
) -> NoteRead:
    """
    Create a note.

    Args:
        payload: NoteCreate with title and content.
        session: Async database session.
        user: Current user.

    Returns:
        NoteRead: Created note.
    """
    note = Note(user_id=user.id, title=payload.title, content=payload.content)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return NoteRead.model_validate(note)


# PUBLIC_INTERFACE
@router.get(
    "/{id}",
    response_model=NoteRead,
    summary="Retrieve a specific note",
    description="Retrieve note by ID if owned by current user.",
)
async def get_note(
    id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_preview_or_current_user),
) -> NoteRead:
    """
    Get a specific note by ID for the current user.

    Args:
        id: Note ID.
        session: Async database session.
        user: Current user.

    Returns:
        NoteRead: The requested note.

    Raises:
        HTTPException: 404 if not found or not owned by user.
    """
    result = await session.execute(select(Note).where(Note.id == id, Note.user_id == user.id))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


# PUBLIC_INTERFACE
@router.put(
    "/{id}",
    response_model=NoteRead,
    summary="Update a note",
    description="Update title and content of a note owned by the current user.",
)
async def update_note(
    id: int,
    payload: NoteUpdate,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_preview_or_current_user),
) -> NoteRead:
    """
    Update a note.

    Args:
        id: Note ID.
        payload: NoteUpdate.
        session: Async DB session.
        user: Current user.

    Returns:
        NoteRead: Updated note.

    Raises:
        HTTPException: 404 if not found.
    """
    result = await session.execute(select(Note).where(Note.id == id, Note.user_id == user.id))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = payload.title
    note.content = payload.content
    await session.commit()
    await session.refresh(note)
    return NoteRead.model_validate(note)


# PUBLIC_INTERFACE
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Delete a note owned by the current user.",
)
async def delete_note(
    id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_preview_or_current_user),
) -> None:
    """
    Delete a note.

    Args:
        id: Note ID.
        session: Async DB session.
        user: Current user.

    Returns:
        None with 204 status.
    """
    result = await session.execute(select(Note).where(Note.id == id, Note.user_id == user.id))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    await session.delete(note)
    await session.commit()
    return None


# PUBLIC_INTERFACE
@router.get(
    "/{id}/summary",
    response_model=SummaryRead,
    summary="Retrieve summary for a specific note",
    description="Fetch a stored summary for the note if available.",
)
async def get_note_summary(
    id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_preview_or_current_user),
) -> SummaryRead:
    """
    Retrieve stored summary for a note.

    Args:
        id: Note ID.
        session: Async DB session.
        user: Current user.

    Returns:
        SummaryRead: Stored summary.

    Raises:
        HTTPException: 404 if not found.
    """
    # Ensure note ownership
    result = await session.execute(select(Note).where(Note.id == id, Note.user_id == user.id))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    sres = await session.execute(select(Summary).where(Summary.note_id == id))
    summary = sres.scalar_one_or_none()
    if summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    return SummaryRead.model_validate(summary)


# PUBLIC_INTERFACE
@router.post(
    "/{id}/summarize",
    summary="Generate summary for a note",
    description="Trigger AI summarization for the note. Stores the result and returns it.",
)
async def summarize_note(
    id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_preview_or_current_user),
) -> dict:
    """
    Trigger AI summarization for a note, persisting the summary.

    Args:
        id: Note ID.
        session: Async DB session.
        user: Current user.

    Returns:
        dict: { "summary": "<text>" }

    Raises:
        HTTPException: 404 if note not found.
    """
    # Ensure note ownership
    result = await session.execute(select(Note).where(Note.id == id, Note.user_id == user.id))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    client = SummarizationClient()
    summary_text = await client.summarize(note_id=str(note.id), content=note.content)

    # Upsert summary
    sres = await session.execute(select(Summary).where(Summary.note_id == id))
    existing = sres.scalar_one_or_none()
    if existing:
        existing.summary_text = summary_text
    else:
        new_summary = Summary(note_id=id, summary_text=summary_text)
        session.add(new_summary)

    await session.commit()
    return {"summary": summary_text}
