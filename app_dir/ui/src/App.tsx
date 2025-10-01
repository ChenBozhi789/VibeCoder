import { useState, useEffect } from 'react';
import { Header } from './components/organisms/Header';
import { NewTaskInput } from './components/molecules/NewTaskInput';
import { TaskList } from './components/organisms/TaskList';
import { Footer } from './components/organisms/Footer';
import type { Task } from './types';

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);

  // Load tasks from localStorage on mount
  useEffect(() => {
    try {
      const savedTasks = localStorage.getItem('hope-todo-tasks');
      if (savedTasks) {
        setTasks(JSON.parse(savedTasks));
      }
    } catch (err) {
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  // Save tasks to localStorage whenever tasks change
  useEffect(() => {
    if (!loading) {
      try {
        localStorage.setItem('hope-todo-tasks', JSON.stringify(tasks));
      } catch (err) {
        setError('Failed to save tasks');
      }
    }
  }, [tasks, loading]);

  // Load theme from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('hope-todo-theme') as 'light' | 'dark' | null;
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('hope-todo-theme', theme);
  }, [theme]);

  const handleAddTask = (title: string) => {
    const newTask: Task = {
      id: crypto.randomUUID(),
      title: title.trim(),
      completed: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setTasks(prev => [newTask, ...prev]);
  };

  const handleToggleComplete = (id: string) => {
    setTasks(prev =>
      prev.map(task =>
        task.id === id
          ? { ...task, completed: !task.completed, updatedAt: new Date().toISOString() }
          : task
      )
    );
  };

  const handleEditTask = (id: string, title: string) => {
    setTasks(prev =>
      prev.map(task =>
        task.id === id
          ? { ...task, title: title.trim(), updatedAt: new Date().toISOString() }
          : task
      )
    );
    setEditingTaskId(null);
  };

  const handleDeleteTask = (id: string) => {
    setTasks(prev => prev.filter(task => task.id !== id));
  };

  const handleThemeToggle = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header 
        onThemeToggle={handleThemeToggle}
        isDarkMode={theme === 'dark'}
      />
      
      <main className="container mx-auto px-4 py-6 max-w-2xl">
        <NewTaskInput onSubmit={handleAddTask} disabled={loading} />
        
        <div className="mt-6">
          <TaskList
            tasks={tasks}
            onToggle={handleToggleComplete}
            onEdit={handleEditTask}
            onDelete={handleDeleteTask}
            loading={loading}
            error={error}
            editingTaskId={editingTaskId}
            onStartEdit={setEditingTaskId}
          />
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;