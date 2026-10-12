export interface Employee {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  department: string;
  job_title: string;
  joining_date: string;
  probation_end_date: string | null;
  hr_verified: boolean;
  location: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}
export type EmployeeWrite = Omit<Employee, 'id' | 'created_at' | 'updated_at' | 'hr_verified' | 'location'> & { hr_verified?: boolean; location?: string | null };
