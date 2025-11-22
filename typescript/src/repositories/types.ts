// Base entity interface matching existing patterns
export interface BaseRecord {
  id: string | number;
  createdAt?: string;
  updatedAt?: string;
}

// Query parameters matching useCustomDataProvider structure
export interface GetListParams {
  pagination?: {
    current?: number;
    pageSize?: number;
  };
  sorters?: Array<{
    field: string;
    order: "asc" | "desc";
  }>;
  filters?: Array<{
    field: string;
    operator: string;
    value: unknown;
  }>;
}

export interface GetOneParams {
  id: string | number;
}

export interface GetManyParams {
  ids: Array<string | number>;
}

export interface CreateParams<TVariables = Record<string, unknown>> {
  variables: TVariables;
}

export interface UpdateParams<TVariables = Record<string, unknown>> {
  id: string | number;
  variables: TVariables;
}

export interface DeleteOneParams {
  id: string | number;
}

// Response types matching existing API patterns
export interface GetListResponse<TData extends BaseRecord = BaseRecord> {
  data: TData[];
  total: number;
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
  };
}

export interface GetOneResponse<TData extends BaseRecord = BaseRecord> {
  data: TData;
}

export interface GetManyResponse<TData extends BaseRecord = BaseRecord> {
  data: TData[];
}

export interface CreateResponse<TData extends BaseRecord = BaseRecord> {
  data: TData;
}

export interface UpdateResponse<TData extends BaseRecord = BaseRecord> {
  data: TData;
}

export interface DeleteOneResponse<TData extends BaseRecord = BaseRecord> {
  data: TData;
}

// Utility types for create/update operations
export type CreateInput<T> = Omit<T, "id" | "createdAt" | "updatedAt">;
export type UpdateInput<T> = Partial<CreateInput<T>>;
