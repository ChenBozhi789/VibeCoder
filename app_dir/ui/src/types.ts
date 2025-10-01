// TypeScript interfaces for HopeTodo UI prototype

export interface Task {
  id: string;
  title: string;
  completed: boolean;
  createdAt: string; // ISO8601
  updatedAt: string; // ISO8601
}

export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'ghost' | 'outline';
  size?: 'sm' | 'default' | 'lg';
  onClick?: () => void;
  disabled?: boolean;
  ariaLabel?: string;
  className?: string;
}

export interface InputProps {
  id: string;
  label?: string;
  value?: string;
  placeholder?: string;
  onChange?: (value: string) => void;
  hint?: string;
  type?: string;
  className?: string;
}

export interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}

export interface TaskCardProps {
  task: Task;
  onView?: (id: string) => void;
  onToggleComplete?: (id: string) => void;
  className?: string;
}

export interface TaskListProps {
  tasks: Task[];
  onView?: (id: string) => void;
  onToggleComplete?: (id: string) => void;
  className?: string;
}
