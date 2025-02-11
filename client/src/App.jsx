import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Encrypt from "./components/Encrypt";
import Decrypt from "./components/Decrypt";
import Layout from "./components/ui/Layout";

const App = () => {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/encrypt" element={<Encrypt />} />
        <Route path="/decrypt" element={<Decrypt />} />
      </Routes>
    </Layout>
  );
}

export default App;
