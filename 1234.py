import streamlit as st
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np

# --- 1. การเตรียมชุดข้อมูลและการฝึกโมเดล (เหมือนเดิม) ---

# ชุดข้อมูลตัวอย่าง
data = {
    'Age': [25, 45, 19, 30, 50, 22, 35, 28, 55, 30],
    'Weight': [60, 95, 55, 110, 70, 80, 105, 65, 85, 120],
    'Height': [1.70, 1.75, 1.65, 1.80, 1.60, 1.85, 1.72, 1.68, 1.70, 1.80],
    'FHWO': [0, 1, 0, 1, 1, 0, 1, 0, 1, 1], # Family History with Overweight: 1=Yes, 0=No
    'FAVC': [0, 1, 0, 1, 1, 0, 1, 0, 1, 1], # Frequent High Calorie Food: 1=Yes, 0=No
    'FAF': [3, 1, 2, 0, 1, 2, 0, 3, 1, 0],  # Physical Activity Frequency: 0-3
    'Obesity_Level': ['N', 'O', 'IW', 'O', 'OW', 'OW', 'O', 'N', 'OW', 'O'] # Target
}
df = pd.DataFrame(data)

X = df.drop('Obesity_Level', axis=1)
y = df['Obesity_Level']

# Label Encoding
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Training Model
model = DecisionTreeClassifier(random_state=42)
model.fit(X, y_encoded)

# ฟังก์ชันทำนาย
def predict_obesity_level(age, weight, height, fhwo, favc, faf):
    # โมเดลปัจจุบันไม่ได้ใช้ 'Gender' ในการทำนาย ดังนั้นจึงใช้เพียงคุณสมบัติที่มีอยู่
    new_data = pd.DataFrame({
        'Age': [age],
        'Weight': [weight],
        'Height': [height],
        'FHWO': [fhwo],
        'FAVC': [favc],
        'FAF': [faf]
    })
    prediction_encoded = model.predict(new_data)
    prediction_label = le.inverse_transform(prediction_encoded)
    return prediction_label[0]

# --- 2. การสร้างหน้าเว็บด้วย Streamlit ---

st.set_page_config(page_title="Obesity Predictor", layout="wide") # เพิ่มการตั้งค่าหน้าเว็บ

st.title("ระบบทำนายความเสี่ยงภาวะอ้วน (Obesity Predictor)")
st.markdown("กรุณากรอกข้อมูลเพื่อประเมินความเสี่ยงภาวะอ้วนของคุณโดยใช้ Machine Learning.")

# --- 3. การรับ Input จากผู้ใช้ (Widgets) ---

# ใช้ st.columns เพื่อจัดให้ Input อยู่เคียงข้างกัน
col1, col2, col3 = st.columns(3)

with col1:
    age = st.slider("อายุ (Age)", 15, 65, 30, help="ช่วงอายุที่แนะนำ: 15 ถึง 65 ปี")
    
    # เพิ่มตัวเลือกเพศตามคำขอ
    gender = st.selectbox(
        "เพศ (Gender)",
        ["ชาย", "หญิง"],
        index=0,
        help="ข้อมูลเพศถูกเพิ่มเพื่อบันทึก แต่ไม่ได้ถูกใช้ในการทำนายโดยโมเดลปัจจุบัน"
    )
    
with col2:
    weight = st.number_input("น้ำหนัก (kg)", 30.0, 200.0, 70.0, step=0.1, format="%.1f")
    height = st.number_input("ส่วนสูง (m)", 1.0, 2.5, 1.70, step=0.01, format="%.2f")

with col3:
    # การเลือกแบบ Radio สำหรับประวัติครอบครัว
    fhwo_option = st.radio(
        "มีประวัติครอบครัวอ้วน (FHWO)?", 
        ["ไม่มี", "มี"], 
        index=0, 
        horizontal=True
    )
    # การเลือกแบบ Radio สำหรับอาหารแคลอรี่สูง
    favc_option = st.radio(
        "กินอาหารแคลอรี่สูงบ่อย (FAVC)?", 
        ["ไม่บ่อย", "บ่อย"], 
        index=0, 
        horizontal=True
    )

# การรับ Input แบบ Slider สำหรับค่าที่เป็นสเกล
faf = st.slider(
    "ความถี่ในการออกกำลังกาย (FAF) (ต่อสัปดาห์)", 
    0, 
    7, 
    2, 
    help="0=ไม่เคยออกกำลังกาย, 7=ออกกำลังกายทุกวัน"
)

# แปลงค่าจาก Input ของ Streamlit เป็นตัวเลขที่โมเดลเข้าใจ
fhwo_encoded = 1 if fhwo_option == "มี" else 0
favc_encoded = 1 if favc_option == "บ่อย" else 0
# แปลงความถี่ต่อสัปดาห์ให้เป็นสเกล 0-3 (โดยประมาณ) เพื่อให้สอดคล้องกับชุดข้อมูลตัวอย่าง
# การแปลง: 0-7 วัน ถูกแมปเป็น 0-3 (0: 0วัน, 1: 1-2วัน, 2: 3-4วัน, 3: 5-7วัน)
if faf == 0:
    faf_scaled = 0
elif faf <= 2:
    faf_scaled = 1
elif faf <= 4:
    faf_scaled = 2
else:
    faf_scaled = 3

# แสดงค่าที่ใช้ในการทำนาย (เฉพาะส่วนที่ถูกแปลงแล้ว)
st.sidebar.subheader("ค่าที่ใช้ในการทำนาย (Encoded)")
st.sidebar.write(f"Age: {age}, Gender: {gender}, Weight: {weight}, Height: {height}")
st.sidebar.write(f"FHWO (ประวัติครอบครัว): {fhwo_encoded}")
st.sidebar.write(f"FAVC (อาหารแคลอรี่สูง): {favc_encoded}")
st.sidebar.write(f"FAF (ออกกำลังกาย, สเกล 0-3): {faf_scaled}")


# --- 4. ปุ่มทำนายและแสดงผลลัพธ์ ---

st.markdown("---")

if st.button("🌟 ทำนายความเสี่ยง", use_container_width=True):
    # ทำนายผล
    try:
        prediction = predict_obesity_level(
            age, 
            weight, 
            height, 
            fhwo_encoded, 
            favc_encoded, 
            faf_scaled
        )
        
        # การแสดงผล
        st.subheader("📊 ผลการทำนายความเสี่ยงภาวะอ้วน")
        
        level_map = {
            'IW': {'text': 'น้ำหนักน้อย (Insufficient Weight)', 'color': 'blue'},
            'N': {'text': 'น้ำหนักปกติ (Normal Weight)', 'color': 'green'},
            'OW': {'text': 'น้ำหนักเกิน (Overweight)', 'color': 'orange'},
            'O': {'text': 'ภาวะอ้วน (Obesity Type I/II/III)', 'color': 'red'}
        }
        
        result_info = level_map.get(prediction, {'text': 'ไม่สามารถระบุได้', 'color': 'gray'})
        
        # ใช้ markdown เพื่อจัดรูปแบบข้อความ
        st.markdown(
            f"""
            <div style='
                padding: 15px; 
                border-radius: 10px; 
                text-align: center; 
                background-color: {result_info['color']}1A; 
                border: 2px solid {result_info['color']};
            '>
                <h3 style='color: {result_info['color']}; margin: 0;'>
                    ระดับที่ทำนาย: {result_info['text']}
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.write("---")
        
        # คำแนะนำตามผลลัพธ์
        if prediction == 'N':
            st.success("✅ คำแนะนำเบื้องต้น: ยอดเยี่ยม! รักษารูปแบบการใช้ชีวิตที่ดีต่อสุขภาพนี้ไว้ต่อไป")
            st.balloons()
            
        elif prediction == 'IW':
            st.info("💡 คำแนะนำเบื้องต้น: ควรเน้นการบริโภคอาหารที่มีคุณค่าทางโภชนาการและพลังงานให้เพียงพอต่อความต้องการของร่างกาย")
            
        elif prediction in ['OW', 'O']:
            st.warning("⚠️ คำแนะนำเบื้องต้น: คุณมีความเสี่ยงสูง ควรปรึกษาแพทย์หรือนักโภชนาการเพื่อวางแผนการจัดการน้ำหนัก เพิ่มการออกกำลังกาย และปรับเปลี่ยนพฤติกรรมการรับประทานอาหารให้สม่ำเสมอ")
            
        else:
            st.info("คำแนะนำเบื้องต้น: ข้อมูลยังไม่เพียงพอต่อการให้คำแนะนำที่เฉพาะเจาะจง กรุณาปรึกษาผู้เชี่ยวชาญ")

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการทำนาย: {e}")

# Footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        color: gray;
        text-align: center;
        padding: 10px;
        font-size: 0.8em;
    }
    </style>
    <div class="footer">
        หมายเหตุ: การทำนายนี้ใช้โมเดล Decision Tree จากชุดข้อมูลตัวอย่างขนาดเล็ก ควรปรึกษาแพทย์เพื่อการวินิจฉัยที่ถูกต้อง
    </div>
    """,
    unsafe_allow_html=True
)