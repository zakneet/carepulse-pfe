import { Component } from '@angular/core';
@Component({ selector:'app-analytics', templateUrl:'./analytics.component.html', styleUrls:['./analytics.component.css'] })
export class AnalyticsComponent {
  kpis = [
    { label:'Total Appointments',  value:'1,284', trend:'+12%', color:'blue' },
    { label:'Patient Satisfaction', value:'96.4%', trend:'+2.1%', color:'green' },
    { label:'Average Wait Time',   value:'14 min', trend:'-6 min', color:'cyan' },
    { label:'Cancellation Rate',   value:'3.2%',  trend:'-1.1%', color:'violet' },
  ];
  monthlyData = [75,82,91,88,95,78,100,93,87,94,98,88];
  months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  maxBar = 100;
}
