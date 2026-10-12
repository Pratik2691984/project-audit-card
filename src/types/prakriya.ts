export type SutraType = 'samjna' | 'vidhi' | 'niyama' | 'adhikara' | 'atidesha' | 'paribhasa';

export interface SutraRef {
  number: string;
  name: string;
  type: SutraType;
}

export interface DerivationStepJSON {
  step_index: number;
  rule_applied: SutraRef;
  left_operand: string;
  right_operand: string;
  output: string;
  metadata?: Record<string, string>;
  is_ekadesha?: boolean;
}

export interface PrakriyaPayload {
  root_left: string;
  root_right: string;
  gana_name: string;
  gana_number: number;
  final_output: string;
  steps: DerivationStepJSON[];
}