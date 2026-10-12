import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Employee, EmployeeWrite } from './employee.model';
import { EmployeeService } from './employee.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './app.component.html'
})
export class AppComponent implements OnInit {
  private readonly api = inject(EmployeeService);
  private readonly fb = inject(FormBuilder);
  employees: Employee[] = [];
  selectedId: number | null = null;
  search = '';
  department = '';
  allDepartments: string[] = [];
  role = localStorage.getItem('ems-demo-role') || 'HR';
  loading = false;
  saving = false;
  error = '';
  success = '';
  readonly form = this.fb.nonNullable.group({
    employee_code: ['', [Validators.required, Validators.maxLength(30), Validators.pattern(/^[A-Za-z0-9_-]+$/)]],
    first_name: ['', [Validators.required, Validators.maxLength(80)]],
    last_name: ['', [Validators.required, Validators.maxLength(80)]],
    email: ['', [Validators.required, Validators.email, Validators.maxLength(254)]],
    department: ['', [Validators.required, Validators.maxLength(100)]],
    job_title: ['', [Validators.required, Validators.maxLength(100)]],
    joining_date: ['', Validators.required],
    probation_end_date: [''],
    location: ['', Validators.maxLength(100)],
    hr_verified: [false]
  });

  ngOnInit(): void { this.load(); }
  get isHr(): boolean { return this.role === 'HR'; }
  get selectedEmployee(): Employee | undefined {
    return this.selectedId == null ? undefined : this.employees.find(e => e.id === this.selectedId);
  }
  removeSelected(): void {
    const employee = this.selectedEmployee;
    if (employee) this.remove(employee);
  }
  load(): void {
    this.loading = true; this.error = '';
    const unfiltered = !this.search.trim() && !this.department;
    this.api.list(this.search, this.department).subscribe({
      next: rows => {
        this.employees = rows; this.loading = false;
        const found = rows.map(e => e.department);
        // Unfiltered load is the full set: replace. Narrowed loads only add, never shrink.
        this.allDepartments = this.distinctSorted(unfiltered ? found : [...this.allDepartments, ...found]);
      },
      error: err => { this.error = this.errorMessage(err); this.loading = false; }
    });
  }
  onSearch(value: string): void { this.search = value; this.load(); }
  onDepartmentChange(value: string): void { this.department = value; this.load(); }
  get departments(): string[] { return this.allDepartments; }
  private distinctSorted(values: string[]): string[] {
    const seen = new Map<string, string>();
    for (const v of values) if (v && !seen.has(v.toLowerCase())) seen.set(v.toLowerCase(), v);
    return [...seen.values()].sort((a, b) => a.localeCompare(b));
  }
  changeRole(value: string): void {
    this.role = value; localStorage.setItem('ems-demo-role', value);
  }
  newEmployee(): void {
    this.selectedId = null; this.success = ''; this.error = '';
    this.form.reset({employee_code:'',first_name:'',last_name:'',email:'',department:'',job_title:'',joining_date:'',probation_end_date:'',location:'',hr_verified:false});
  }
  edit(employee: Employee): void {
    this.selectedId = employee.id; this.success = ''; this.error = '';
    this.form.reset({
      employee_code: employee.employee_code, first_name: employee.first_name,
      last_name: employee.last_name, email: employee.email, department: employee.department,
      job_title: employee.job_title, joining_date: employee.joining_date,
      probation_end_date: employee.probation_end_date ?? '',
      location: employee.location ?? '',
      hr_verified: employee.hr_verified ?? false
    });
  }
  save(): void {
    this.error = ''; this.success = '';
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const value = this.form.getRawValue();
    if (value.probation_end_date && value.probation_end_date < value.joining_date) {
      this.error = 'Probation end date cannot be before joining date.'; return;
    }
    const payload: EmployeeWrite = {...value, probation_end_date: value.probation_end_date || null, location: value.location || null};
    this.saving = true;
    const request = this.selectedId ? this.api.update(this.selectedId, payload) : this.api.create(payload);
    request.subscribe({
      next: employee => {
        this.success = `Employee ${employee.employee_code} saved successfully.`;
        this.saving = false; this.load(); this.edit(employee);
      },
      error: err => { this.error = this.errorMessage(err); this.saving = false; }
    });
  }
  clearProbationDate(): void {
    if (!this.isHr || !this.selectedId) return;
    this.api.updateProbationDate(this.selectedId, null).subscribe({
      next: updated => { this.success = 'Probation end date cleared.'; this.edit(updated); this.load(); },
      error: err => this.error = this.errorMessage(err)
    });
  }
  onHrVerifiedToggle(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    if (!this.isHr) { this.form.controls.hr_verified.setValue(!checked); return; }
    // New record: keep local value; it is sent with the create POST.
    if (!this.selectedId) { this.form.controls.hr_verified.setValue(checked); return; }
    this.error = ''; this.success = '';
    this.api.updateHrVerified(this.selectedId, checked).subscribe({
      next: updated => {
        this.employees = this.employees.map(e => e.id === updated.id ? updated : e);
        this.form.controls.hr_verified.setValue(updated.hr_verified);
        this.success = `HR verified ${updated.hr_verified ? 'set' : 'cleared'}.`;
      },
      error: err => {
        this.form.controls.hr_verified.setValue(!checked);
        this.error = this.errorMessage(err);
      }
    });
  }
  remove(employee: Employee): void {
    if (!confirm(`Delete ${employee.first_name} ${employee.last_name}?`)) return;
    this.api.delete(employee.id).subscribe({
      next: () => { this.success = 'Employee deleted.'; if (this.selectedId === employee.id) this.newEmployee(); this.load(); },
      error: err => this.error = this.errorMessage(err)
    });
  }
  private errorMessage(err: unknown): string {
    if (err instanceof HttpErrorResponse) {
      const detail = err.error?.detail;
      return typeof detail === 'string' ? detail : detail?.message || `Request failed (${err.status}). Is the API running?`;
    }
    return 'Unexpected error. Please try again.';
  }
}
