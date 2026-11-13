# ExamPilot 2.0 — Storage Migration Guide

**Company:** GT InnoX LLP  
**Product:** ExamPilot 2.0 — *Understand Questions. Learn the Answers.*  
**Branch:** `security/production-readiness-remediation`  
**Date:** November 14, 2026  

---

## 1. Overview & Architectural Motivation

In prior iterations, study documents were written directly to local disk (`backend/storage/documents/`). In cloud deployments (Render, Railway, Fly.io, Heroku, or AWS ECS), container file systems are ephemeral. Any container restart or redeploy caused document loss, and multi-replica setups could not access files uploaded to peer instances.

To solve this, ExamPilot 2.0 introduces a pluggable **Durable Storage Abstraction** (`BaseStorageService` in `backend/app/services/storage.py`) supporting:
1. **`LocalStorageService`**: Safe, user-isolated local directory storage for development, testing, and dedicated persistent Linux VMs.
2. **`SupabaseStorageService`**: Production durable object storage using Supabase Storage private buckets with user-isolated object keys and signed URLs.

---

## 2. Database Schema Representation

The `documents` table includes two dedicated columns managed by Alembic migration `0002_security_hardening`:
- `storage_provider`: `VARCHAR(30) NOT NULL DEFAULT 'local'` (e.g. `'local'`, `'supabase'`, `'s3'`).
- `storage_key`: `VARCHAR(500) NULL` (e.g. `'documents/{user_id}/{document_id}.pdf'`).

---

## 3. Configuring Supabase Storage for Production

### Step 1: Create the Storage Bucket in Supabase
1. Log into your **Supabase Dashboard** &rarr; **Storage**.
2. Click **New Bucket**.
3. Name: `exampilot-documents`.
4. Visibility: **Private** (Disable Public Bucket). Only backend service credentials or signed URLs can access objects.

### Step 2: Configure Environment Variables
Set the following secrets in your production host (Render/Railway):
```env
STORAGE_PROVIDER=supabase
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[YOUR-SERVICE-ROLE-KEY]
SUPABASE_STORAGE_BUCKET=exampilot-documents
```

---

## 4. Migration Strategy for Existing Local Documents

For teams migrating pre-existing local documents to Supabase Storage:

1. **Run Database Migration:**
   ```bash
   python -m alembic upgrade head
   ```
2. **Execute Object Sync Script:**
   A utility script can iterate over existing records where `storage_provider = 'local'` and upload the file from `storage_path` into the Supabase bucket:
   ```python
   # Migration snippet
   from backend.app.db.session import SessionLocal
   from backend.app.db.models import Document
   from backend.app.services.storage import SupabaseStorageService

   supabase_storage = SupabaseStorageService()
   db = SessionLocal()

   local_docs = db.query(Document).filter(Document.storage_provider == "local").all()
   for doc in local_docs:
       if os.path.exists(doc.storage_path):
           with open(doc.storage_path, "rb") as f:
               content = f.read()
           meta = supabase_storage.save_file(
               user_id=doc.user_id,
               document_id=doc.id,
               filename=doc.filename,
               content_bytes=content
           )
           doc.storage_provider = "supabase"
           doc.storage_key = meta["storage_key"]
           doc.storage_path = meta["storage_path"]
   db.commit()
   db.close()
   ```
3. Existing records remain fully readable and operable during and after migration.

---

## 5. Security Invariants Maintained

- **Private Buckets Only:** Documents are never exposed to public internet URLs.
- **User Tenant Isolation:** Objects are saved under `documents/{user_id}/{document_id}.pdf`.
- **Atomic Deletion:** Deleting a document via `/api/documents/{id}` automatically purges both the database chunks and the remote storage object.
