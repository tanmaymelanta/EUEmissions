import streamlit as st
import pandas as pd
import numpy as np
from streamlit import expander

st.set_page_config(page_title="Fuel EU Calculator", layout="wide")
st.title("EU Maritime Calculator")

def fuel_eu(df, fuel_cols=None):
    new_df = df[df['Leg Category'].isin(['Into the EU', 'Out of the EU', 'Within EU'])].reset_index(drop=True)
    total_energy_in_scope = new_df['Total Energy Consumed In Scope'].sum()
    fuel_dict = {}
    for fuel in fuel_cols:
        if f"{fuel}_LCV" in fuel_cols:
            wtw = new_df[f"{fuel}_WtT"].mean() + new_df[f"{fuel}_TtW"].mean()
            fuel_dict[fuel] = (new_df[fuel].sum(), new_df[f"{fuel}_LCV"].mean(), new_df[f"{fuel}_WtT"].mean(), new_df[f"{fuel}_TtW"].mean(), wtw)
    sorted_fuel = sorted(fuel_dict.items(), key=lambda item: item[1][4], reverse=False)
    temp = total_energy_in_scope
    new_dict = {}
    for i in sorted_fuel:
        fuel, lcv, wtt, ttw, wtw = i[1][0], i[1][1]*1000000, i[1][2], i[1][3], i[1][4]
        nw_fuel = temp / lcv if fuel > 0 and temp > 0 else 0
        nw_fuel = fuel if nw_fuel > fuel else nw_fuel
        temp = temp - nw_fuel * lcv if fuel > 0 and temp > 0 else temp
        new_dict[i[0]] = [nw_fuel, lcv, wtt, ttw, wtw]
    return total_energy_in_scope, new_dict

def eu_ets(df, fuel_cols=None):
    new_df = df[df['Leg Category'].isin(['Into the EU', 'Out of the EU', 'Within EU'])].reset_index(drop=True)
    new_df["Emissions"] = 0
    for fuel in fuel_cols:
        if f"{fuel}_CO2" in fuel_cols:
            new_df["Emissions"] += new_df[fuel] * new_df[f"{fuel}_CO2"]
    new_df['EUA'] = np.where(new_df['Leg Category'].values == 'Within EU', new_df['Emissions'].values, np.where(np.isin(new_df['Leg Category'].values, ['Into the EU', 'Out of the EU']), new_df['Emissions'].values * 0.5, 0)) * 0.7
    eua = new_df['EUA'].sum()
    return eua, new_df

def biofuel():
    with expander("Bunker Details", True):
        if "blend_rows" not in st.session_state:
            st.session_state.blend_rows = [0]

        def add_blend_row_below(index):
            st.session_state.blend_rows.insert(index + 1, max(st.session_state.blend_rows) + 1)

        def remove_blend_row(index):
            if len(st.session_state.blend_rows) > 1:
                st.session_state.blend_rows.pop(index)

        for j, blend_row_id in enumerate(st.session_state.blend_rows):
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1.5, 1.5, 1.25, 2, 2, 2, 2])
            with col1:
                st.selectbox("Blend Fuel", ['HFO', 'LFO', 'MGO'], key=f"blend_{blend_row_id}")
            with col2:
                blend = st.number_input(f"Total Blend Fuel {j} (MT) (From BDN)", key=f"blend_input_{blend_row_id}", format="%.3f")
            with col3:
                st.selectbox("Bio Fuel", ['Bio-diesel', 'HVO'], key=f"bio_{blend_row_id}")
            with col4:
                bio = st.number_input(f"Bio Fuel {j} (MT) (From POS) ", key=f"bio_input_{blend_row_id}", format="%.3f")
            with col5:
                st.number_input(f"Energy from Bio Fuel Component {j} (MJ) (From POS)", key=f"energy_input_{blend_row_id}", format="%.3f")
            with col6:
                st.number_input(f"Bio Fuel Component Intensity {j} (gCO2e/MJ) (From POS)", key=f"intensity_input_{blend_row_id}", format="%.3f")
            with col7:
                add, remove = st.columns([1, 1.5])
                with add:
                    st.markdown("<body style='font-size:15px;'>Add Row</body>", unsafe_allow_html=True)
                    if st.button("➕", key=f"add_blend_row_{blend_row_id}", use_container_width=True):
                        add_blend_row_below(j)
                with remove:
                    st.markdown("<body style='font-size:15px;'>Remove Row</body>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"remove_blend_row_{blend_row_id}", use_container_width=True):
                        remove_blend_row(j)
            with col8:
                st.markdown("<body style='font-size:15px;'>Bio Fuel</body>", unsafe_allow_html=True)
                st.markdown("<body style='font-size:15px;'></body>", unsafe_allow_html=True)
                st.write(f"B{bio/blend*100:02.0f}" if (blend) != 0 and blend >= bio else "Error")

        blend_data = []
        for blend_row_id in st.session_state.blend_rows:
            bio_fuel_type = st.session_state.get(f"bio_{blend_row_id}", "")
            intensity_input = st.session_state.get(f"intensity_input_{blend_row_id}", 0.0)
            bio_input = st.session_state.get(f"bio_input_{blend_row_id}", 0.0)
            energy_input = st.session_state.get(f"energy_input_{blend_row_id}", 0.0)
            ttw = 78.07811 if bio_fuel_type == "Bio-diesel" else (72.04295 if bio_fuel_type == "HVO" else 0.0)
            wtt = intensity_input-ttw if intensity_input != 0 else (-61.69459 if bio_fuel_type == "Bio-diesel" else -54.79545 if bio_fuel_type == "HVO" else 0.0)
            lcv = energy_input / bio_input if bio_input != 0 else 0.0
            row_data = {
                "Bio Bunker": blend_row_id,
                "Blend Fuel Type": st.session_state.get(f"blend_{blend_row_id}", 0.0),
                "blend": st.session_state.get(f"blend_input_{blend_row_id}", 0.0),
                "Bio Fuel Type": bio_fuel_type,
                "bio": bio_input,
                "energy": energy_input,
                "LCV": lcv,
                "WtT": wtt,
                "TtW": ttw,
                "CO2": 0,
            }
            blend_data.append(row_data)
        blend_df = pd.DataFrame(blend_data)
        valid_mask = (
                (blend_df['blend'] != 0) &
                (blend_df['blend'] >= blend_df['bio']) &
                (blend_df['blend'] != "")
        )
        blend_df['Fuel/Engine'] = "Error"
        valid_blend_ratio = (100 * blend_df.loc[valid_mask, 'bio'] / blend_df.loc[valid_mask, 'blend']).round(0)
        blend_df.loc[valid_mask, 'Fuel/Engine'] = "B" + valid_blend_ratio.astype(int).astype(str).str.zfill(2)
        blend_df = blend_df[blend_df['Fuel/Engine'] != "Error"]
        blend_df["key"] = blend_df['Bio Bunker'].astype(str) +"_"+ blend_df['Fuel/Engine'].astype(str)
    return blend_df

def lng(engine_types):
    lng_df = pd.DataFrame({"Fuel/Engine": ["LNG Boiler [slip-0%]", "LNG Diesel (dual fuel slow speed) [slip-0.2%]", "LNG Otto (dual fuel slow speed) [slip-1.7%]", "LNG LBSI [slip-2.6%]", "LNG Otto (dual fuel medium speed) [slip-3.1%]"], 
                           "LCV": [0.0491, 0.0491, 0.0491, 0.0491, 0.0491], 
                           "WtT": [18.5, 18.5, 18.5, 18.5, 18.5], 
                           "TtW": [56.68, 57.58074, 64.36808, 68.44048, 70.70293], 
                           "CO2": [2.75, 2.75, 2.75, 2.75, 2.75]})
    lng_df = lng_df[lng_df['Fuel/Engine'].isin(engine_types)].reset_index(drop=True)
    return lng_df

def columns_helper(bioFuelState, lng_engine_list):
    if bioFuelState == "Yes":
        blend_df = biofuel()
    else:
        blend_df = pd.DataFrame(
            {"Fuel/Engine": [], "Bio Bunker": [], "Blend Fuel Type": [], "LCV": [], "WtT": [], "TtW": [], "CO2": []})

    if lng_engine_list != []:
        lng_df = lng(engine_types=lng_engine_list)
    else:
        lng_df = pd.DataFrame({"Fuel/Engine": [], "LCV": [], "WtT": [], "TtW": [], "CO2": []})
    columns_df = pd.concat([blend_df, lng_df], ignore_index=True)
    columns_df['Bio Bunker'] = round(columns_df['Bio Bunker'].fillna(0), 0).astype(int)
    return columns_df

with st.expander("Vessel/Voyage Information",True):
    col1, col2 = st.columns(2)
    with col1:
        bio_fuel = st.selectbox("Bio Fuel Used in voyage", ["No", "Yes"], key="bio_fuel")
    with col2:
        lng_engine_type = st.multiselect("LNG Engine Type", ["LNG Boiler [slip-0%]", "LNG Diesel (dual fuel slow speed) [slip-0.2%]", "LNG Otto (dual fuel slow speed) [slip-1.7%]", "LNG LBSI [slip-2.6%]", "LNG Otto (dual fuel medium speed) [slip-3.1%]"], key="lng_engine_type")

columns_df = columns_helper(bioFuelState=st.session_state.bio_fuel, lng_engine_list=st.session_state.lng_engine_type)

with expander("Voyage Details", True):
    if "rows" not in st.session_state:
        st.session_state.rows = [0]

    def add_row_below(index):
        st.session_state.rows.insert(index + 1, max(st.session_state.rows) + 1)

    def remove_row(index):
        if len(st.session_state.rows) > 1:
            st.session_state.rows.pop(index)

    for i, row_id in enumerate(st.session_state.rows):
        cols = [3, 1.5, 1.5, 1.5, 1.5, 1.5] + [1.5] * len(columns_df) + [2.5]
        columns = st.columns(cols)

        col1, col2, col3, col4, col5, col6, *dynamic_cols, col8 = columns
        with col1:
            st.selectbox("Leg Category", ['Into the EU', 'Out of the EU', 'Within EU', 'Outside EU'], key=f"leg_category_{row_id}")
        with col2:
            st.number_input("HFO", key=f"hfo_input_{row_id}", format="%.3f")
        with col3:
            st.number_input("LFO", key=f"lfo_input_{row_id}", format="%.3f")
        with col4:
            st.number_input("MDO", key=f"mdo_input_{row_id}", format="%.3f")
        with col5:
            st.number_input("LPG P", key=f"lpgp_input_{row_id}", format="%.3f")
        with col6:
            st.number_input("LPG B", key=f"lpgb_input_{row_id}", format="%.3f")
        for col, fuel, bunker in zip(dynamic_cols, columns_df['Fuel/Engine'], columns_df['Bio Bunker']):
            if "LNG" in fuel:
                with col:
                    st.number_input(f"{fuel}", key=f"lng_{fuel}_{row_id}", format="%.3f")
            else:
                with col:
                    st.number_input(f"Bunker {bunker} {fuel}", key=f"bio_bunker_{bunker}_{row_id}", format="%.3f")
        with col8:
            add, remove = st.columns([1, 1.5])
            with add:
                st.markdown("<body style='font-size:15px;'>Add Row</body>", unsafe_allow_html=True)
                if st.button("➕", key=f"add_row_{row_id}", use_container_width=True):
                    add_row_below(i)
            with remove:
                st.markdown("<body style='font-size:15px;'>Remove Row</body>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"remove_row_{row_id}", use_container_width=True):
                    remove_row(i)

if st.button("Calculate",use_container_width=True):
    st.markdown("&nbsp;", unsafe_allow_html=True)
    data = []
    for row_id in st.session_state.rows:
        row_data = {
            "Leg Category": st.session_state.get(f"leg_category_{row_id}", ""),
            "HFO": st.session_state.get(f"hfo_input_{row_id}", 0.0), #MT
            "LFO": st.session_state.get(f"lfo_input_{row_id}", 0.0), #MT
            "MDO": st.session_state.get(f"mdo_input_{row_id}", 0.0), #MT
            "LPG P": st.session_state.get(f"lpgp_input_{row_id}", 0.0), #MT
            "LPG B": st.session_state.get(f"lpgb_input_{row_id}", 0.0), #MT
            "HFO_LCV": 0.0405, #MJ/g
            "LFO_LCV": 0.041, #MJ/g
            "MDO_LCV": 0.0427, #MJ/g
            "LPG P_LCV": 0.046, #MJ/g
            "LPG B_LCV": 0.046, #MJ/g
            "HFO_WtT": 13.5, #WtTco2eq/MJ
            "LFO_WtT": 13.2, #WtTco2eq/MJ
            "MDO_WtT": 14.4, #WtTco2eq/MJ
            "LPG P_WtT": 7.8, #WtTco2eq/MJ
            "LPG B_WtT": 7.8, #WtTco2eq/MJ
            "HFO_TtW": 78.2442, #TtWco2eq/MJ
            "LFO_TtW": 78.19244, #TtWco2eq/MJ
            "MDO_TtW": 76.36745, #TtWco2eq/MJ
            "LPG P_TtW": 66.41065, #TtWco2eq/MJ
            "LPG B_TtW": 67.06283, #TtWco2eq/MJ
            "HFO_CO2": 3.114, #CO2/Fuel
            "LFO_CO2": 3.151, #CO2/Fuel
            "MDO_CO2": 3.206, #CO2/Fuel
            "LPG P_CO2": 3, #CO2/Fuel
            "LPG B_CO2": 3.03, #CO2/Fuel
        }
        for fuel, bunker, type, lcv, WtT, TtW, co2 in (zip(columns_df['Fuel/Engine'], columns_df['Bio Bunker'], columns_df['Blend Fuel Type'], columns_df['LCV'], columns_df['WtT'], columns_df['TtW'], columns_df['CO2'])):
            if "LNG" in fuel:
                row_data[f"{fuel}"] = st.session_state.get(f"lng_{fuel}_{row_id}", 0.0)
                row_data[f"{fuel}_LCV"] = lcv
                row_data[f"{fuel}_WtT"] = WtT
                row_data[f"{fuel}_TtW"] = TtW
                row_data[f"{fuel}_CO2"] = co2
            else:
                key = f"bio_bunker_{bunker}_{row_id}"
                row_data[f"{bunker}_{fuel}"] = st.session_state.get(key, 0.0)*(int(fuel[1:])/100)
                row_data[type] += st.session_state.get(key, 0.0)*(1-(int(fuel[1:])/100))
                row_data[f"{bunker}_{fuel}_LCV"] = lcv
                row_data[f"{bunker}_{fuel}_WtT"] = WtT
                row_data[f"{bunker}_{fuel}_TtW"] = TtW
                row_data[f"{bunker}_{fuel}_CO2"] = 0
        data.append(row_data)
    df = pd.DataFrame(data)

    fuel_cols = [col for col in df.columns]
    products = []
    for fuel_col in fuel_cols:
        lcv_col = fuel_col + '_LCV'
        if lcv_col in df.columns:
            products.append(df[fuel_col] * 1000000 * df[lcv_col])
    df['Total Energy Consumed'] = pd.concat(products, axis=1).sum(axis=1)

    df['Total Energy Consumed In Scope'] = np.where(df['Leg Category'].values == 'Within EU',
                                                    df['Total Energy Consumed'].values, np.where(
            np.isin(df['Leg Category'].values, ['Into the EU', 'Out of the EU']),
            df['Total Energy Consumed'].values * 0.5, 0))
    
    st.dataframe(df[[col for col in df.columns if not col.endswith('_LCV') and not col.endswith('_WtT') and not col.endswith('_TtW') and not col.endswith('_CO2')]])
    eua, eu_ets_df = eu_ets(df=df, fuel_cols=fuel_cols)
    total_energy_in_scope, new_fuel_dict = fuel_eu(df=df, fuel_cols=fuel_cols)

    test_df = pd.DataFrame(new_fuel_dict)
    Well_to_Tank_GHG = round((test_df.iloc[0] * test_df.iloc[2] * test_df.iloc[1]).sum() / total_energy_in_scope if total_energy_in_scope != 0 else 0, 5) #WtT GHG Intensity = ( MT x 1,000,000 x 'WtTco2eq/MJ' x LCV ) / MJ
    Tank_to_Wake_GHG = round((test_df.iloc[0] * test_df.iloc[3] * test_df.iloc[1]).sum() / total_energy_in_scope if total_energy_in_scope != 0 else 0, 5) #TtW GHG Intensity = ( MT x 1,000,000 x 'TtWco2eq/MJ' x LCV) / MJ
    Well_to_Wake = round(Well_to_Tank_GHG + Tank_to_Wake_GHG, 5)
    compliance_balance = round((89.3368 - Well_to_Wake) * total_energy_in_scope, 1)
    penalty = 0 if compliance_balance > 0 else round(abs((compliance_balance / Well_to_Wake) * (2400 / 41000)),0)

    left, right = st.columns([1.5, 2])

    with left:
        st.markdown("### FUEL EU", unsafe_allow_html=True)
        output_text = f"""
Total Energy In Scope: {total_energy_in_scope:,.0f} MJ

Fuel EU Consumption (MT):
"""
        for fuel in new_fuel_dict:
            if new_fuel_dict[fuel][0] > 0:
                output_text += f"  - {fuel}: {new_fuel_dict[fuel][0]:.3f} MT\n"
        output_text += f"""
Well to Tank GHG Intensity: {Well_to_Tank_GHG} gCO2eq/MJ 
Tank to Wake GHG Intensity: {Tank_to_Wake_GHG} gCO2eq/MJ
Total Well to Wake GHG Intensity: {Well_to_Wake} gCO2eq/MJ
Compliance Balance: {compliance_balance / 1e6:,.2f} x 10⁶ gCO2eq
Penalty: €{penalty:,.0f}
"""
        st.code(output_text, language="text")

    with right:
        st.markdown("### EU ETS", unsafe_allow_html=True)
        st.code(f"Total EUA: {eua:,.2f}", language="text")
        st.dataframe(eu_ets_df[[col for col in eu_ets_df.columns if not col.endswith('_LCV') and not col.endswith('_WtT') and not col.endswith('_TtW') and not col.endswith('_CO2') and not col.endswith('Total Energy Consumed') and not col.endswith('Total Energy Consumed In Scope')]], hide_index=True)

    with expander("Bunker Price ($/MT)", True):
        df = pd.read_csv("data/bunker_prices.csv")
        st.dataframe(df, hide_index=True)
