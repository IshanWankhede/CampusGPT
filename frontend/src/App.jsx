import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import AppRoutes from "./routes/AppRoutes";
import SmoothCursor from "./features/prototype-visuals/SmoothCursor";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <SmoothCursor />
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}