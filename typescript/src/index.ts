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

// API Client
export { BaseApiService, ERROR_CODES } from "./client/BaseApiService";
export type { ApiErrorData } from "./client/BaseApiService";

// Repository Pattern
export { BaseCrudRepository } from "./repositories/BaseCrudRepository";
export type * from "./repositories/types";
