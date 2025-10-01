import React from "react";
import { Button } from "../components/button";
import Input from "../components/input";
import TaskList from "../components/task-list";
import { Task } from "../components/task-card";

/**
 * ListPage - presentational with placeholder data and callbacks
 * Default export to match App.tsx's import pattern.
 */

const sampleTasks: Task[] = [
  { id: "1", title: "Buy groceries", description: "Milk, eggs, bread", dueDate: "Today", completed: false },
  { id: "2", title: "Walk dog", description: "20 min walk in park", dueDate: "Today 6pm", completed: false },
];

const ListPage: React.FC = () => {
  // No logic: presentational placeholders only
  const [search] = React.useState("");
  const onView = (id: string) => {
    // placeholder: host should wire navigation
    console.log("view", id);
  };
  const onToggle = (id: string) => {
    console.log("toggle", id);
  };

  return (
    <div>
      <div className="card" style={{display:"flex", flexDirection:"column", gap:12, marginBottom:16}}>
        <div style={{display:"flex", gap:12, alignItems:"center", flexWrap:"wrap"}}>
          <Input id="search" label="Search" placeholder="Search tasks..." value={search} onChange={() => {}} />
          <div style={{marginLeft:"auto", display:"flex", gap:8}}>
            <Button variant="ghost" onClick={() => console.log("filter")}>Filter</Button>
            <Button variant="primary" onClick={() => console.log("add")}>Add</Button>
          </div>
        </div>
      </div>

      <section aria-labelledby="tasks-heading">
        <h2 id="tasks-heading" style={{marginBottom:12}}>Tasks</h2>
        <TaskList tasks={sampleTasks} onView={onView} onToggleComplete={onToggle} />
        <div style={{marginTop:12}} className="pagination" aria-hidden>
          <span style={{color:"var(--color-muted)"}}>Showing {sampleTasks.length} tasks</span>
        </div>
      </section>
    </div>
  );
};

export default ListPage;
