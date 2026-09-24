## Rollback Plan for Antenna DGS Predictor (v1.0.0 Launch)

### Trigger Conditions
- 5xx Error rate > 2x baseline on `/api/predict`
- FastAPI `lifespan` failure (models failing to load on boot in production)
- User reports of UI Canvas crashing on load

### Rollback Steps
1. The frontend (Vite/React) and backend (FastAPI) are stateless. Deploy previous stable commit:
   `git checkout v0.9.0 && git push origin main`
2. Restart the production API instance.
3. Verify rollback: check the `GET /api/health` endpoint returns 200.
4. Communicate: notify the team of the rollback in #engineering-announcements.

### Database Considerations
- None. The application operates purely on request payload calculations and loaded ML artifact files (`.joblib`). There is no persistent production database that requires schema migrations or backwards-compatibility fixes.

### Time to Rollback
- Redeploy previous version: < 2 minutes (Stateless Node/Python restart).
