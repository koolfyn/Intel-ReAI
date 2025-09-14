import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Subreddit from './pages/Subreddit';
import Post from './pages/Post';
import CreateSubreddit from './pages/CreateSubreddit';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/r/:subredditName" element={<Subreddit />} />
          <Route path="/posts/:postId" element={<Post />} />
          <Route path="/create-subreddit" element={<CreateSubreddit />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
