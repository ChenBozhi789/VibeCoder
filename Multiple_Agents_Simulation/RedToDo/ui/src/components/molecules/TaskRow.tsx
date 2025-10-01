import React from 'react';
import { Task } from '../types';
interface TaskRowProps {
  task: Task;
  onToggle?: (id: string)=>void;
  onEdit?: (task: Task)=>void;
}
export const TaskRow: React.FC<TaskRowProps> = ({ task, onToggle, onEdit }) => {
  return (
    <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px',borderBottom:'1px solid #f0f0f0'}}>
      <div style={{display:'flex',alignItems:'center',gap:12}}>
        <input aria-label={`Mark ${task.title} done`} type="checkbox" checked={task.done} onChange={()=>onToggle && onToggle(task.id)} />
        <div>
          <div style={{fontSize:16, textDecoration: task.done ? 'line-through' : 'none'}}>{task.title}</div>
          {task.dueDate && <div style={{fontSize:12,color:'#666'}}>Due: {task.dueDate}</div>}
        </div>
      </div>
      <div>
        <button aria-label="Edit task" onClick={()=>onEdit && onEdit(task)} style={{border:'none',background:'transparent',cursor:'pointer'}}>✎</button>
      </div>
    </div>
  );
};
export default TaskRow;
