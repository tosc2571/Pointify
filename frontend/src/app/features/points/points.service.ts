import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Point, PointType } from '../../core/models';

export interface PointCreatePayload {
  type: PointType;
  text: string;
  rating: number;
}

@Injectable({ providedIn: 'root' })
export class PointsService {
  constructor(private readonly http: HttpClient) {}

  create(subthemeId: number, payload: PointCreatePayload): Observable<Point> {
    return this.http.post<Point>(`/api/subthemes/${subthemeId}/points`, payload);
  }

  update(subthemeId: number, pointId: number, payload: PointCreatePayload): Observable<Point> {
    return this.http.patch<Point>(`/api/subthemes/${subthemeId}/points/${pointId}`, payload);
  }

  delete(subthemeId: number, pointId: number): Observable<void> {
    return this.http.delete<void>(`/api/subthemes/${subthemeId}/points/${pointId}`);
  }
}
