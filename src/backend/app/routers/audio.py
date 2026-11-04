from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import audio_service as svc
from ..database import get_db
from ..deps import current_user
from ..models import AudioAnalysis, AudioReference, User

router = APIRouter(prefix="/audio", tags=["Audio Detector"])
MAX_BYTES = 25 * 1024 * 1024


async def _read(upload: UploadFile) -> bytes:
    data = await upload.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File too large (max 25 MB)")
    return data


@router.post("/upload-reference", status_code=201)
async def upload_reference(file: UploadFile = File(...), user: User = Depends(current_user),
                           db: Session = Depends(get_db)):
    try:
        fp = svc.encode(svc.fingerprint(svc.load_wav(await _read(file))))
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    ref = AudioReference(user_id=user.id, audio_fingerprint=fp)  # the file itself is not retained
    db.add(ref)
    db.commit()
    return {"reference_id": ref.id}


@router.post("/analyze")
async def analyze(file: UploadFile = File(...), reference_id: int | None = Form(default=None),
                  user: User = Depends(current_user), db: Session = Depends(get_db)):
    ref_fp = None
    if reference_id is not None:
        ref = db.get(AudioReference, reference_id)
        if not ref or ref.user_id != user.id:
            raise HTTPException(404, "Reference not found")
        ref_fp = ref.audio_fingerprint
    try:
        status, sim, details = svc.analyse(ref_fp, await _read(file))
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    row = AudioAnalysis(user_id=user.id, detected_status=status, similarity_score=sim)
    db.add(row)
    db.commit()
    return {"report_id": row.id, "status": status, "similarity": round(sim, 3), "details": details}


@router.get("/history")
def history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(AudioAnalysis).where(AudioAnalysis.user_id == user.id)
                      .order_by(AudioAnalysis.analysis_date.desc()).limit(200)).all()
    return [{"report_id": r.id, "status": r.detected_status, "similarity": r.similarity_score,
             "analysis_date": r.analysis_date} for r in rows]


@router.get("/report/{report_id}")
def report(report_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    r = db.get(AudioAnalysis, report_id)
    if not r or r.user_id != user.id:
        raise HTTPException(404, "Report not found")
    return {"report_id": r.id, "status": r.detected_status, "similarity": r.similarity_score,
            "analysis_date": r.analysis_date}
