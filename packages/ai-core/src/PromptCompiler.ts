export interface SystemDirectives {
  architectureStyle: string;
  namingConvention: string;
  themeColors: string[];
}

export class PromptCompiler {
  public static compileSystemPrompt(specialistPartId: number, baseInstruction: string): string {
    return `=== BEVHUB AI SPECIALIST ROLE (PART ${specialistPartId}) ===\n${baseInstruction}\n========================`;
  }

  public static injectContextDirectives(prompt: string, directives: SystemDirectives): string {
    const formattedStyles = `
[Design System Directives]
Architecture: ${directives.architectureStyle}
Naming Style: ${directives.namingConvention}
Theme Palette: ${directives.themeColors.join(', ')}
`;
    return `${formattedStyles}\n\n[User Goal Prompt]\n${prompt}`;
  }

  public static mergeTemplates(baseHtml: string, componentInject: string): string {
    if (baseHtml.includes('<!-- components -->')) {
      return baseHtml.replace('<!-- components -->', componentInject);
    }
    return baseHtml + '\n' + componentInject;
  }
}
