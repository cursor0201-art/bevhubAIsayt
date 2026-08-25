export interface ValidationResult {
  success: boolean;
  score: number;
  details: {
    architecture: number;
    security: number;
    performance: number;
    testing: number;
  };
  errors: string[];
}

export class Validator {
  public static validateStep(
    type: string,
    output: any
  ): ValidationResult {
    let architecture = 95;
    let security = 95;
    let performance = 95;
    let testing = 95;
    const errors: string[] = [];

    // Simple code validation checks
    if (type === 'frontend') {
      const html = String(output.html || '');
      if (!html.includes('<!DOCTYPE html>')) {
        architecture -= 20;
        errors.push('Missing HTML5 DOCTYPE declaration.');
      }
      if (!html.includes('<header') || !html.includes('<footer')) {
        architecture -= 15;
        errors.push('Missing semantic header or footer elements.');
      }
      if (!html.includes('id=')) {
        security -= 10;
        errors.push('Interactive components missing unique IDs.');
      }
    }

    if (type === 'database') {
      const sql = String(output.sql || '');
      if (sql.toLowerCase().includes('password') && !sql.toLowerCase().includes('encrypted')) {
        security -= 30;
        errors.push('Plaintext credentials or keys found in DDL schemas.');
      }
    }

    const overallScore = Math.round((architecture + security + performance + testing) / 4);

    return {
      success: overallScore >= 90 && errors.length === 0,
      score: overallScore,
      details: { architecture, security, performance, testing },
      errors
    };
  }

  // Self repair simulator
  public static repair(
    type: string,
    failedOutput: any,
    errors: string[]
  ): { repairedOutput: any; repairReasoning: string } {
    console.log(`[Validator] Self-Repair loop: correcting ${type} step with errors: ${errors.join(', ')}`);
    
    let repairedOutput = { ...failedOutput };
    let repairReasoning = 'Auto-injected corrections to satisfy quality gates.';

    if (type === 'frontend') {
      let html = String(failedOutput.html || '');
      if (!html.includes('<!DOCTYPE html>')) {
        html = '<!DOCTYPE html>\n' + html;
      }
      if (!html.includes('<header')) {
        html = html.replace('<body>', '<body>\n<header id="main-header">Header content</header>');
      }
      if (!html.includes('<footer')) {
        html = html.replace('</body>', '<footer id="main-footer">Footer content</footer>\n</body>');
      }
      repairedOutput.html = html;
    }

    if (type === 'database') {
      let sql = String(failedOutput.sql || '');
      sql = sql.replace(/password/gi, 'password_hash TEXT');
      repairedOutput.sql = sql;
    }

    return { repairedOutput, repairReasoning };
  }
}
