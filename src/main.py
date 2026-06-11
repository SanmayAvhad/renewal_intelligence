from google import genai
from dataloader import load_data
import logging
import os
from dotenv import load_dotenv

from reconcile import parse_csm_notes
from feature_engineering import build_master_feature_table
from llm_features import build_csm_feature_table, build_nps_feature_table
from changelog_intelligence import build_changelog_features
from risk_scoring import build_risk_report
from explanations import build_explanation_report, save_final_report
from insights import generate_insights, save_insights
from config import OUTPUT_DIR
from loggerfile import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

data = load_data()
accounts_df = data["accounts"]
usage_df = data["usage"]
tickets_df = data["tickets"]
nps_df = data["nps"]
csm_notes_text = data["csm_notes"]

structured_csm_df = parse_csm_notes( notes_text=csm_notes_text, accounts_df=accounts_df)
csm_features_df = build_csm_feature_table( structured_csm_df, batch_size=10 )
nps_features_df = build_nps_feature_table( nps_df, batch_size=10 )

logger.info("\nBuilding account features...")
master_df = build_master_feature_table( accounts_df=accounts_df, usage_df=usage_df, ticket_df=tickets_df, csm_features_df=csm_features_df, nps_features_df=nps_features_df, )
logger.info( f"Master rows before merge: {len(master_df)}" )

logger.info("\nApplying changelog intelligence...")
master_df = build_changelog_features(master_df)   
master_df.to_csv( f"{OUTPUT_DIR}/master_features.csv", index=False )

logger.info("\nCalculating renewal risk...")
risk_report_df = build_risk_report( master_df, renewal_column="contract_end_date" )
risk_report_df.to_csv( f"{OUTPUT_DIR}/risk_report.csv", index=False )
logger.info( f"Accounts renewing soon: {len(risk_report_df)}" )

insights_df = generate_insights(risk_report_df)
save_insights(insights_df)
logger.info("\nKey Insights")
logger.info( insights_df[ [ "title", "description" ] ] )

logger.info("\nGenerating explanations...")
final_report_df = ( build_explanation_report( risk_report_df, batch_size=10 ) )
save_final_report( final_report_df, f"{OUTPUT_DIR}/final_risk_report.csv" )
logger.info("Explanation generation complete")

logger.info("\nTop Renewal Risks\n")
preview_cols = [ "account_name", "risk_score", "risk_tier" ]
available_cols = [ col for col in preview_cols if col in final_report_df.columns ]

logger.info( final_report_df[ available_cols ] .head(10) .to_string(index=False) )
logger.info( f"\nPipeline complete." )

