import React from "react";
import Card from "./card";
import { Button } from "./button";

export interface Task {
  id: string;
  title: string;
  description?: string;
  dueDate?: string;
  completed?: boolean;
}

export interface TaskCardProps {
  task: Task;
  onView?: (id: string) => void;
  onToggleComplete?: (id: string) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onView, onToggleComplete }) => {
  return (
    <Card className="task-card" title={task.title} subtitle={task.dueDate}>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", gap:12}}>
        <div style={{flex:1}}>
          <div style={{color: "var(--color-muted)", marginBottom:8}}>{task.description || "No description"}</div>
        </div>
        <div style={{display:"flex", gap:8, alignItems:"center"}}>
          <Button variant="ghost" onClick={() => onView?.(task.id)} ariaLabel={`View ${task.title}`}>View</Button>
          <Button variant="primary" onClick={() => onToggleComplete?.(task.id)} ariaLabel={`Toggle complete ${task.title}`}>
            {task.completed ? "Undo" : "Complete"}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default TaskCard;
