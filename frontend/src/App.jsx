import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import AppRoutes from "./routes/AppRoutes";
import SmoothCursor from "./features/prototype-visuals/SmoothCursor";
import GlobalSmoothScroll from "./features/prototype-visuals/GlobalSmoothScroll";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <GlobalSmoothScroll>
          <SmoothCursor />
          <AppRoutes />
        </GlobalSmoothScroll>
      </AuthProvider>
    </BrowserRouter>
  );
}