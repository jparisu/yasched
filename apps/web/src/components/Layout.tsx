import { useState } from "react";
import { Sidebar } from "./Sidebar";
import { Dashboard } from "./pages/Dashboard";
import { Topics } from "./pages/Topics";
import { Agenda } from "./pages/Agenda";
import { TaskBoard } from "./pages/TaskBoard";
import { Calendar } from "./pages/Calendar";

type Page = "dashboard" | "topics" | "agenda" | "tasks" | "calendar";

function renderPage(page: Page) {
  switch (page) {
    case "dashboard":
      return <Dashboard />;
    case "topics":
      return <Topics />;
    case "agenda":
      return <Agenda />;
    case "tasks":
      return <TaskBoard />;
    case "calendar":
      return <Calendar />;
  }
}

export function Layout() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");

  return (
    <div className="flex h-screen bg-background">
      <div className="flex-shrink-0">
        <Sidebar currentPage={currentPage} onPageChange={(p) => setCurrentPage(p as Page)} />
      </div>
      <main className="flex-1 overflow-auto">{renderPage(currentPage)}</main>
    </div>
  );
}
