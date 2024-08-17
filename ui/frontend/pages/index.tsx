import Dashboard from '@/components/dashboard/dashboard'
import type { NextPage } from 'next'

const Home: NextPage = () => {
  return (
    <div className="container mx-auto pt-10" style={{ "widows": 1 }}>
      <Dashboard />
    </div>
  )
}

export default Home
