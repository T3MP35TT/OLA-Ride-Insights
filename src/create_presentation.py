"""Generate the capstone deck from the processed project data and EDA charts."""
from pathlib import Path
import pandas as pd
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR

ROOT=Path(__file__).resolve().parents[1]
TEAL=RGBColor(18,151,129); NAVY=RGBColor(20,48,66); PALE=RGBColor(238,247,246); WHITE=RGBColor(255,255,255)
def main():
    df=pd.read_csv(ROOT/"data/processed/ola_cleaned.csv")
    prs=Presentation(); prs.slide_width= Inches(13.333); prs.slide_height= Inches(7.5)
    blank=prs.slide_layouts[6]
    def textbox(slide,x,y,w,h,text,size=20,color=NAVY,bold=False):
        shape=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=shape.text_frame; tf.word_wrap=True
        for i,line in enumerate(text.split("\n")):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.text=line; p.font.size=Pt(size); p.font.bold=bold; p.font.color.rgb=color; p.space_after=Pt(9)
        return shape
    def slide(title,sub=None):
        s=prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb=WHITE
        bar=s.shapes.add_shape(1,0,0,prs.slide_width,Inches(.18)); bar.fill.solid(); bar.fill.fore_color.rgb=TEAL; bar.line.fill.background()
        textbox(s,.65,.42,12, .6,title,28,NAVY,True)
        if sub: textbox(s,.67,1.05,12,.45,sub,12,TEAL)
        return s
    def bullets(s,items,x=.8,y=1.7,w=11.7,size=20): textbox(s,x,y,w,5.2,"\n".join("•  "+t for t in items),size)
    s=prs.slides.add_slide(blank); s.background.fill.solid(); s.background.fill.fore_color.rgb=NAVY
    textbox(s,.8,1.4,11.8,1.1,"OLA RIDE INSIGHTS",36,WHITE,True); textbox(s,.85,2.8,11,1.2,"End-to-end ride analytics\nJuly 2024 booking dataset",23,RGBColor(170,235,218))
    textbox(s,.85,6.4,11,.4,"Python  •  SQL  •  Power BI specifications  •  Streamlit",15,WHITE)
    status=df.Booking_Status.value_counts(); n=len(df); success=int(status.get("Success",0)); cust=int(status.get("Canceled by Customer",0)); driver=int(status.get("Canceled by Driver",0)); nf=int(status.get("Driver Not Found",0)); successdf=df[df.Booking_Status.eq("Success")]
    s=slide("Business problem","Use operational data to improve supply matching and customer experience")
    bullets(s,["When does demand peak and how does it vary by vehicle?","Where do cancellations and driver-not-found outcomes occur?","How do booking value, payment preference and ratings vary?","Separate completed booking value from all-status booking value."])
    s=slide("Objectives and use cases")
    bullets(s,["Measure hourly demand to inform driver allocation.","Compare vehicle mix, distance and completed booking value.","Separate customer cancellations, driver cancellations and driver-not-found bookings.","Support operational decisions with reproducible Python, SQL and BI definitions."])
    s=slide("Dataset overview",f"Source workbook: OLA_DataSet.xlsx  |  {n:,} records × 20 source columns  |  {df.Booking_ID.nunique():,} unique booking IDs")
    bullets(s,["Fields include date/time, booking/customer IDs, status, vehicle, locations, TAT measures, cancellation reasons, payment, value, distance and ratings.","July 1–31, 2024; 4 booking outcomes.","No exact duplicate rows or duplicate booking IDs.","39,057 records lack ratings, consistent with non-success outcomes; null feedback remains null."])
    s=slide("Technology and workflow")
    bullets(s,["Excel source preserved unchanged.","Pandas profiling, cautious cleaning and derived date/status features.","SQL business questions and Python reconciliation.","Power BI model and DAX specification; Streamlit application with CSV fallback."])
    s=slide("Data quality and cleaning",f"{n:,} rows retained  |  0 exact duplicate rows removed  |  0 duplicate booking IDs")
    bullets(s,["Ratings, booking outcomes and reason fields are not imputed.","Cancellation fields contain reason text, not yes/no indicators.","Vehicle Images is a formula-backed presentation field and is omitted from the analytical CSV.","No outliers are silently dropped; see profile and cleaning audit."])
    s=slide("Booking outcomes",f"Success {success:,} ({success/n:.2%})  |  Customer cancel {cust:,} ({cust/n:.2%})  |  Driver cancel {driver:,} ({driver/n:.2%})  |  Driver not found {nf:,} ({nf/n:.2%})")
    bullets(s,["Denominator is all 103,024 booking rows.","Driver Not Found remains distinct from customer and driver cancellations.","Completed booking value uses Success rows only."])
    for title,file in [("Demand by hour","bookings_by_hour.png"),("Booking status and vehicle mix","booking_status.png"),("Cancellation reasons","driver_cancel_reason.png"),("Vehicle distance","distance_by_vehicle.png")]:
        s=slide(title)
        img=ROOT/"reports/eda_charts"/file
        if img.exists(): s.shapes.add_picture(str(img), Inches(1.1), Inches(1.55), width=Inches(10.9), height= Inches(5.1))
    s=slide("SQL and validation","Ten required questions plus additional operations and finance-oriented analyses")
    bullets(s,["Queries use exact status labels and the dataset's reason-text fields.","All ten required queries were executed through SQLite-compatible query validation.","SQL results for key counts and completed value reconcile to independent pandas calculations.","MySQL server was not configured; schema/load scripts remain ready for a MySQL environment."],size=18)
    s=slide("Power BI dashboard specification","Aligned to the supplied Ola-Slides reference deck")
    bullets(s,["Overall: ride volume over time and status breakdown.","Vehicle Type: top five vehicle types by distance and the reference KPIs.","Revenue: payment method, top customers and daily ride distance.","Cancellation: separate customer and driver reasons/trends.","Ratings: driver/customer distributions and comparison."],size=17)
    s=slide("Streamlit application")
    bullets(s,["Eight navigation views: overview, rides, revenue, cancellations, ratings, SQL explorer, data explorer and Power BI integration.","Search, interactive charts, filtered CSV download and local CSV/workbook fallback.","Database is optional; no credentials are hardcoded."])
    s=slide("Key findings and action areas")
    bullets(s,[f"Highest booking volume vehicle: {df.Vehicle_Type.value_counts().idxmax()}.",f"Most frequent recorded payment: {df.Payment_Method.value_counts().idxmax()}.",f"Peak booking hour: {int(df['Booking Hour'].value_counts().idxmax()):02d}:00.",f"Completed booking value: {successdf.Booking_Value.sum():,.0f} (source units).",f"Most common driver cancellation reason: {df.loc[df.Booking_Status.eq('Canceled by Driver'),'Canceled_Rides_by_Driver'].mode().iloc[0]}."])
    s=slide("Recommendations")
    bullets(s,["Investigate driver-not-found bookings by pickup location and hour.","Align driver supply with the hourly demand profile and evaluate using a measured pilot.","Address customer and driver cancellation reason leaders through separate workflows.","Use completed bookings when comparing booking value across payment methods or vehicles.","Track rating averages with feedback coverage and successful ride context."] ,size=17)
    s=slide("Challenges, limitations and next steps")
    bullets(s,["One month of records; no causal attribution or lifetime value.","Source does not define units for distance, TAT or currency.","Power BI PBIX and account-backed publication require Power BI Desktop/organization access.","MySQL deployment requires a configured instance and explicit CSV load path.","Review documentation, run the app, then validate dashboards in the target account."],size=17)
    s=slide("Conclusion")
    bullets(s,["The source data now has a reproducible, auditable analysis workflow.","Outcome definitions distinguish success, two cancellation categories and driver-not-found.","The dashboard and app handoff are prepared for local and organization-backed delivery."])
    out=ROOT/"presentation/OLA_RIDE_INSIGHTS_FINAL.pptx"; out.parent.mkdir(exist_ok=True); prs.save(out); print(out)
if __name__=="__main__": main()
