export interface Task {
  id: string;
  title: string;
  notes?: string;
  completed?: boolean;
  created_at?: string;
  updated_at?: string;
}
