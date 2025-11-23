import * as Sentry from "@sentry/nextjs";
import { z } from "zod";

import type { BaseApiService } from "../client/BaseApiService";
import type {
  BaseRecord,
  GetListParams,
  GetOneParams,
  GetManyParams,
  CreateParams,
  UpdateParams,
  DeleteOneParams,
  GetListResponse,
  GetOneResponse,
  GetManyResponse,
  CreateResponse,
  UpdateResponse,
  DeleteOneResponse,
} from "./types";

export abstract class BaseCrudRepository<
  TData extends BaseRecord = BaseRecord,
> {
  abstract readonly resource: string;
  protected apiService: BaseApiService;

  /**
   * Abstract method that concrete repositories must implement to provide
   * a Zod schema for validating their data type at runtime
   */
  protected abstract getDataSchema(): z.ZodSchema<TData>;

  constructor(apiService: BaseApiService) {
    this.apiService = apiService;
  }

  /**
   * Validates API response data using the provided schema
   * @param data The raw API response data to validate
   * @param schema The Zod schema to validate against
   * @returns The validated and parsed data
   * @throws Error with descriptive message if validation fails
   */
  protected validateResponse<T>(data: unknown, schema: z.ZodSchema<T>): T {
    try {
      return schema.parse(data);
    } catch (error) {
      if (error instanceof z.ZodError) {
        const issues = error.issues
          .map((issue) => `${issue.path.join(".")}: ${issue.message}`)
          .join("; ");
        const validationError = new Error(
          `API response validation failed for ${this.resource}: ${issues}`,
        );

        // Log validation failure to console for debugging
        console.error(`[Zod Validation Error] ${this.resource}:`, {
          issues: error.issues,
          rawData: data,
        });

        // Report validation failures to Sentry for monitoring API schema changes
        Sentry.captureException(error, {
          tags: {
            errorType: "zod_validation_failure",
            resource: this.resource,
          },
          extra: {
            rawData: data,
          },
        });

        throw validationError;
      }
      throw error;
    }
  }

  /**
   * Creates response schemas based on the data schema from concrete repository
   */
  protected getResponseSchemas() {
    const dataSchema = this.getDataSchema();

    return {
      getList: z.object({
        data: z.array(dataSchema),
        total: z.number(),
        pagination: z
          .object({
            current: z.number(),
            pageSize: z.number(),
            total: z.number(),
          })
          .optional(),
      }) as z.ZodSchema<GetListResponse<TData>>,
      getOne: z.object({
        data: dataSchema,
      }) as z.ZodSchema<GetOneResponse<TData>>,
      getMany: z.object({
        data: z.array(dataSchema),
      }) as z.ZodSchema<GetManyResponse<TData>>,
      create: z.object({
        data: dataSchema,
      }) as z.ZodSchema<CreateResponse<TData>>,
      update: z.object({
        data: dataSchema,
      }) as z.ZodSchema<UpdateResponse<TData>>,
      deleteOne: z.object({
        data: dataSchema,
      }) as z.ZodSchema<DeleteOneResponse<TData>>,
    };
  }

  /**
   * Get paginated list of items
   */
  async getList(
    params?: GetListParams,
    fetchOptions?: RequestInit,
  ): Promise<GetListResponse<TData>> {
    const { pagination, sorters, filters } = params || {};
    const { current = 1, pageSize = 10 } = pagination || {};

    const queryParams = new URLSearchParams({
      current: current.toString(),
      pageSize: pageSize.toString(),
    });

    // Convert sorters to backend format
    if (sorters && sorters.length > 0) {
      const sortArray = sorters.map((sorter) => [
        sorter.field,
        sorter.order === "asc" ? "asc" : "desc",
      ]);
      queryParams.append("sort", JSON.stringify(sortArray));
    }

    // Convert filters to backend format
    if (filters && filters.length > 0) {
      queryParams.append("filters", JSON.stringify(filters));
    }

    const url = `${this.apiService.buildUrl(
      this.resource,
    )}?${queryParams.toString()}`;

    const rawResponse = await this.apiService.request(url, fetchOptions);
    const schemas = this.getResponseSchemas();
    return this.validateResponse(rawResponse, schemas.getList);
  }

  /**
   * Get single item by ID
   */
  async getOne(
    params: GetOneParams,
    fetchOptions?: RequestInit,
  ): Promise<GetOneResponse<TData>> {
    const { id } = params;
    const url = `${this.apiService.buildUrl(this.resource)}/${id}`;

    const rawResponse = await this.apiService.request(url, fetchOptions);
    const schemas = this.getResponseSchemas();
    return this.validateResponse(rawResponse, schemas.getOne);
  }

  /**
   * Get multiple items by IDs
   */
  async getMany(
    params: GetManyParams,
    fetchOptions?: RequestInit,
  ): Promise<GetManyResponse<TData>> {
    const { ids } = params;
    const schemas = this.getResponseSchemas();

    const responses = await Promise.all(
      ids.map(async (id) => {
        const url = `${this.apiService.buildUrl(this.resource)}/${id}`;
        const rawResponse = await this.apiService.request(url, fetchOptions);
        return this.validateResponse(rawResponse, schemas.getOne);
      }),
    );

    const finalResponse = { data: responses.map((response) => response.data) };
    return this.validateResponse(finalResponse, schemas.getMany);
  }

  /**
   * Create new item
   */
  async create<TVariables = Record<string, unknown>>(
    params: CreateParams<TVariables>,
  ): Promise<CreateResponse<TData>> {
    const { variables } = params;
    const url = this.apiService.buildUrl(this.resource);

    const rawResponse = await this.apiService.request(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(variables),
    });

    const schemas = this.getResponseSchemas();
    return this.validateResponse(rawResponse, schemas.create);
  }

  /**
   * Update existing item
   */
  async update<TVariables = Record<string, unknown>>(
    params: UpdateParams<TVariables>,
  ): Promise<UpdateResponse<TData>> {
    const { id, variables } = params;
    const url = `${this.apiService.buildUrl(this.resource)}/${id}`;

    const rawResponse = await this.apiService.request(url, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(variables),
    });

    const schemas = this.getResponseSchemas();
    return this.validateResponse(rawResponse, schemas.update);
  }

  /**
   * Delete item by ID
   */
  async deleteOne(params: DeleteOneParams): Promise<DeleteOneResponse<TData>> {
    const { id } = params;
    const url = `${this.apiService.buildUrl(this.resource)}/${id}`;

    const rawResponse = await this.apiService.request(url, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
    });

    const schemas = this.getResponseSchemas();
    return this.validateResponse(rawResponse, schemas.deleteOne);
  }

  /**
   * Build query string from parameters (utility method)
   */
  protected buildQueryString(params: Record<string, unknown>): string {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (typeof value === "object") {
          searchParams.append(key, JSON.stringify(value));
        } else {
          searchParams.append(key, String(value));
        }
      }
    });
    return searchParams.toString() ? `?${searchParams.toString()}` : "";
  }
}
