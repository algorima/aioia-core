/**
 * AIoIA Core - TypeScript/JavaScript infrastructure
 *
 * Core infrastructure for AIoIA projects
 *
 * Current: Barrel export pattern (Git dependency standard)
 * Future: Consider migrating to private npm registry with subpath exports
 *         - Build output (dist/) with .d.ts files
 *         - Subpath exports: "@aioia/core/client", "@aioia/core/repositories"
 *         - Better tree-shaking and explicit module boundaries
 */

// Errors (synced with Python aioia_core.errors)
export {
  ERROR_CODES,
  ApiError,
  ServerError,
  ClientError,
} from "./errors";
export type { ErrorCode } from "./errors";

// API Client
export { BaseApiService } from "./client/BaseApiService";
export type { ApiErrorData } from "./client/BaseApiService";

// Repository Pattern
export { BaseCrudRepository } from "./repositories/BaseCrudRepository";
export type * from "./repositories/types";

// Components
export { LottiePlayer } from "./components/LottiePlayer";
export type { LottiePlayerProps } from "./components/LottiePlayer";
