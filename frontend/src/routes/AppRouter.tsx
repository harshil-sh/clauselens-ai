import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { PageShell } from "../components/PageShell";
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
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
