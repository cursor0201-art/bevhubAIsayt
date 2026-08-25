export type UserSubscriptionTier = 'free' | 'pro' | 'business' | 'enterprise';

export interface ActionTokenCost {
  chat: number;
  component: number;
  landing: number;
  shop: number;
  crm: number;
  deploy: number;
  refactor: number;
  review: number;
}

export interface TransactionRecord {
  id: string;
  actionType: keyof ActionTokenCost;
  tokensConsumed: number;
  timestamp: number;
  status: 'pending' | 'success' | 'rolled_back';
}

export class BillingEngine {
  private tier: UserSubscriptionTier;
  private tokenBalance: number;
  private dailyLimit: number;
  private dailyConsumed: number = 0;
  private transactions: TransactionRecord[] = [];

  private static readonly COSTS: ActionTokenCost = {
    chat: 5,
    component: 25,
    landing: 80,
    shop: 250,
    crm: 400,
    deploy: 50,
    refactor: 120,
    review: 40
  };

  constructor(tier: UserSubscriptionTier, initialBalance: number) {
    this.tier = tier;
    this.tokenBalance = initialBalance;
    this.dailyLimit = this.getMaxDailyLimitForTier(tier);
  }

  private getMaxDailyLimitForTier(tier: UserSubscriptionTier): number {
    switch (tier) {
      case 'free': return 100;
      case 'pro': return 500;
      case 'business': return 2000;
      case 'enterprise': return 10000;
    }
  }

  public getCostForAction(action: keyof ActionTokenCost): number {
    return BillingEngine.COSTS[action];
  }

  public estimateTokens(action: keyof ActionTokenCost, complexityMultiplier: number = 1.0): number {
    const baseCost = this.getCostForAction(action);
    return Math.ceil(baseCost * complexityMultiplier);
  }

  public chargeAction(action: keyof ActionTokenCost, actualComplexityMultiplier: number = 1.0): TransactionRecord {
    const expected = this.estimateTokens(action, actualComplexityMultiplier);
    
    // Rate limit check
    if (this.dailyConsumed + expected > this.dailyLimit) {
      throw new Error(`Daily token rate limit exceeded for tier: ${this.tier.toUpperCase()}`);
    }

    // Balance check
    if (this.tokenBalance < expected) {
      throw new Error('Insufficient token balance to perform this AI operation.');
    }

    this.tokenBalance -= expected;
    this.dailyConsumed += expected;

    const tx: TransactionRecord = {
      id: `tx-${Math.random().toString(36).substr(2, 9)}`,
      actionType: action,
      tokensConsumed: expected,
      timestamp: Date.now(),
      status: 'success'
    };

    this.transactions.push(tx);
    console.log(`[Billing Engine] Charged ${expected} tokens for action: ${action}. Balance: ${this.tokenBalance}`);
    
    return tx;
  }

  public rollbackTransaction(transactionId: string): void {
    const tx = this.transactions.find(t => t.id === transactionId);
    if (!tx) {
      throw new Error('Transaction record not found.');
    }

    if (tx.status === 'rolled_back') {
      return;
    }

    tx.status = 'rolled_back';
    this.tokenBalance += tx.tokensConsumed;
    this.dailyConsumed -= tx.tokensConsumed;

    console.log(`[Billing Engine] Rolled back ${tx.tokensConsumed} tokens for transaction ${transactionId}. Balance restored to: ${this.tokenBalance}`);
  }

  public getTokenBalance(): number {
    return this.tokenBalance;
  }

  public getTransactions(): TransactionRecord[] {
    return this.transactions;
  }
}
