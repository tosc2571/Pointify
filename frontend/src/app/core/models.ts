export interface User {
  id: number;
  username: string;
  is_admin: boolean;
}

export interface Theme {
  id: number;
  title: string;
  created_at: string;
}

export interface ThemeStats {
  total_points: number;
  avg_rating: number;
  pro_count: number;
  contra_count: number;
}

export interface ThemeDetail extends Theme {
  stats: ThemeStats;
}

export interface SubTheme {
  id: number;
  title: string;
  theme_id: number;
}

export type PointType = 'pro' | 'contra';

export interface Point {
  id: number;
  subtheme_id: number;
  user_id: number;
  type: PointType;
  text: string;
  rating: number;
  created_at: string;
}
