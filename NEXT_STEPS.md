# Next Steps & Missing Features

## Known Issues and Missing Capabilities
1. **Frontend-Backend Validation**: Stronger alignment of error messages between the FastAPI backend and Vue3 UI. Occasionally "stealth mode" routes complicate standard error responses for non-authenticated states.
2. **G-Code Optimization**: While functional, path sorting inside `app.api.gcode_generator` could be optimized further to reduce "air travel" (pen movements without drawing) when plotting disjointed SVG paths. 
3. **Cart Persistence**: The Shopping Cart inside the Order Center relies heavily on local state or single-session Pinia stores. Persistent carts across devices using the database need finalizing. 
4. **Caching Subsystem Check**: Celery integration works for primary tasks, but Redis caching (`service_cache_task`) occasionally lacks cache invalidation on edge-case data modifications (e.g., gifts management).
5. **Decoy Landing Robustness**: The root domain (`/`) provides a decoy blog or clock but lacks convincing dynamic content to deter curious guests from probing the domain if deployed publicly.

## Proposed Next Steps

### Development & Enhancement
- **Component Refactoring**: Audit duplicated UI elements in the `components/` vs `views/` directories (`frontend/src/`) and extract reusable components (e.g., Glass UI components).
- **Test Coverage Improvements**: The backend `tests/` directory has scripts testing specific points (e.g., `test_gcode`, `test_black.png`), but a comprehensive automated test suite (Pytest or similar) should be unified to run via CI/CD.
- **Implement Logging**: Transition `backend.log` and standard `logger.info` calls to a structured logging tool for better observability in `AdminSystem.vue`.

### Deployment & Operations
- **Dockerization Workflow**: Standardize the `DHQ` project deployment stack. Provide a clear `docker-compose.yml` to spin up Vue UI (served by Nginx), FastAPI, MongoDB, and Redis effortlessly in isolated containers.
- **Performance Audit**: Check Vue3 build bundle sizes and lazy-load additional features inside `router/index.js` (many components utilize dynamic imports `() => import(...)`, which is good, but chart libraries could be further isolated).
- **Security Check**: Enforce rate-limiting on endpoints (particularly `/api/auth` and `/shadow-garden/login`) to prevent brute-force probing of the "stealth" interface. 
