export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    authorities: string[];
  };
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  authorities: string[];
  primary_authority?: string;
} 