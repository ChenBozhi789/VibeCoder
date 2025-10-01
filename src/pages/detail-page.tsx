import React from "react";
import Card from "../components/card";
import { Button } from "../components/button";

/**
 * DetailPage - presentational detail view.
 * Accepts an id prop in a real app; here we show a static example.
 */

interface Props {
  id?: string;
}

const DetailPage: React.FC<Props> = ({ id = "example-1" }) => {
  // placeholder task detail
  const task = {
    id,
    title: "Example Task",
    description: "Full details of the task would appear here, including notes and history.",
    dueDate: "Tomorrow",
    completed: false,
  };

  return (
    <div>
      <div style={{display:"flex", gap:8, marginBottom:12, alignItems:"center"}}>
        <Button variant="ghost" onClick={() => console.log("back")}>Back</Button>
        <h1 style={{margin:0}}>Task detail</h1>
      </div>

      <Card title={task.title} subtitle={task.dueDate}>
        <p style={{marginTop:8}}>{task.description}</p>
        <div style={{marginTop:12, display:"flex", gap:8}}>
          <Button variant="ghost" onClick={() => console.log("edit")}>Edit</Button>
          <Button variant="primary" onClick={() => console.log("complete")}>Mark complete</Button>
        </div>
      </Card>
    </div>
  );
};

export default DetailPage;
