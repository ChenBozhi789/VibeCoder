export interface Task {
  id: string;
  title: string;
  done: boolean;
  dueDate?: string;
  reminder?: string;
}
