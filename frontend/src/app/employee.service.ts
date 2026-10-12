import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Employee, EmployeeWrite } from './employee.model';

@Injectable({ providedIn: 'root' })
export class EmployeeService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8000/api/employees';
  private headers(): HttpHeaders {
    const role = localStorage.getItem('ems-demo-role') || 'EMPLOYEE';
    return new HttpHeaders({ 'X-User-Role': role });
  }
  list(search = ''): Observable<Employee[]> {
    let params = new HttpParams();
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<Employee[]>(this.baseUrl, { params, headers: this.headers() });
  }
  get(id: number): Observable<Employee> {
    return this.http.get<Employee>(`${this.baseUrl}/${id}`, { headers: this.headers() });
  }
  create(payload: EmployeeWrite): Observable<Employee> {
    return this.http.post<Employee>(this.baseUrl, payload, { headers: this.headers() });
  }
  update(id: number, payload: EmployeeWrite): Observable<Employee> {
    return this.http.put<Employee>(`${this.baseUrl}/${id}`, payload, { headers: this.headers() });
  }
  updateProbationDate(id: number, value: string | null): Observable<Employee> {
    return this.http.patch<Employee>(`${this.baseUrl}/${id}/probation-end-date`,
      { probation_end_date: value }, { headers: this.headers() });
  }
  delete(id: number): Observable<{message: string; id: number}> {
    return this.http.delete<{message: string; id: number}>(`${this.baseUrl}/${id}`, { headers: this.headers() });
  }
}
