import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import AppRoutes from "./routes/AppRoutes";
import SmoothCursor from "./features/prototype-visuals/SmoothCursor";
import GlobalSmoothScroll from "./features/prototype-visuals/GlobalSmoothScroll";
import PageTransitionProvider from "./features/prototype-visuals/PageTransitionProvider";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <GlobalSmoothScroll>
          {/* Stairs Preloader — triggers on every route change */}
          <PageTransitionProvider>
            <SmoothCursor />
            <AppRoutes />
          </PageTransitionProvider>
        </GlobalSmoothScroll>
      </AuthProvider>
    </BrowserRouter>
  );
}