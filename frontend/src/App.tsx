import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Subreddit from './pages/Subreddit';
import Post from './pages/Post';
import CreateSubreddit from './pages/CreateSubreddit';
import SearchResults from './pages/SearchResults';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/r/:subredditName" element={<Subreddit />} />
          <Route path="/posts/:postId" element={<Post />} />
          <Route path="/create-subreddit" element={<CreateSubreddit />} />
          <Route path="/search" element={<SearchResults />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
