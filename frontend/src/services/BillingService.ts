import { APIClient } from './apiClient';

export interface PlanData {
  name: string;
  slug: string;
  monthly_price: string;
  ai_credits: number;
  projects_limit: number;
}

export interface SubscriptionDetails {
  plan_name: string;
  plan_slug: string;
  status: string;
  renewal_date: string;
}

export interface CreditTransactionData {
  id: string;
  provider: string;
  amount: string;
  task: string;
  created_at: string;
}

export interface BillingDashboardData {
  balance: string;
  subscription: SubscriptionDetails;
  plans: PlanData[];
  transactions: CreditTransactionData[];
}

export class BillingService {
  public static async getDashboard(): Promise<BillingDashboardData> {
    return APIClient.get<BillingDashboardData>('/api/billing/dashboard/');
  }

  public static async subscribe(planSlug: string, billingCycle: 'monthly' | 'yearly' = 'monthly'): Promise<{
    message: string;
    plan_name: string;
    status: string;
    renewal_date: string;
  }> {
    return APIClient.post('/api/billing/subscribe/', { plan_slug: planSlug, billing_cycle: billingCycle });
  }

  public static async applyPromo(code: string): Promise<{
    message: string;
    balance: string;
  }> {
    return APIClient.post('/api/billing/promo/', { code });
  }
}
