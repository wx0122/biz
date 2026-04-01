export interface Hospital {
  id: string;
  name: string;
  level: string;
  distance: string;
  image: string;
}

export interface Escort {
  id: string;
  name: string;
  avatar: string;
  rating: number;
  serviceCount: number;
  tags: string[];
}

export interface ServiceType {
  id: string;
  name: string;
  description: string;
  price: number;
  icon: string;
}

export interface TrainingCourse {
  id: string;
  name: string;
  description: string;
  duration: string;
  price: number;
}
