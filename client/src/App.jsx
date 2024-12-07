import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Encrypt from "./components/Encrypt";
import Decrypt from "./components/Decrypt";

const App = () => {
  return (
    <div className="">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/encrypt" element={<Encrypt />} />
        <Route path="/decrypt" element={<Decrypt />} />
      </Routes>
    </div>
  );
}

export default App;
