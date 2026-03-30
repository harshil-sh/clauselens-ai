import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { PageShell } from "../components/PageShell";
import { EmptyState } from "../components/ui/EmptyState";
import { AnalysisPage } from "../pages/AnalysisPage";
import { RecentPage } from "../pages/RecentPage";
import { UploadPage } from "../pages/UploadPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <PageShell />,
    children: [
      { index: true, element: <UploadPage /> },
      { path: "analyses/:documentId", element: <AnalysisPage /> },
      { path: "recent", element: <RecentPage /> },
      {
        path: "*",
        element: <EmptyState title="Page not found" description="Check the URL or return to the main upload flow." />,
      },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
