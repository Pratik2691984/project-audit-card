export interface ProjectAudit {
  id: string;
  name: string;
  directoryName?: string;
  assignedTrack: string;
  completionStage: string;
  passedChecksCount: number;
  scorePercentage: number;
  isHardeningEligible: boolean;
  disposition: string;
  auditor: string;
  configFilePath: string;
  updatedAt: string;
  promotedInBatch: boolean;
  remediationPlan?: string | null;
  details?: Record<string, any>;
  dispositionNotes?: string;
  remediationHistory?: Array<{
    timestamp: string;
    actor: string;
    actionApplied: string;
    planRetired?: boolean;
    targetPackage?: string;
  }>;
}
