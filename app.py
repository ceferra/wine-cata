"""
🍷 La Cata — App de Cata a Ciegas
  streamlit run app.py --server.address 0.0.0.0
  Organizador: /?modo=organizador   |   Participante: /?modo=participante
"""
import streamlit as st
import pandas as pd
import qrcode, io, base64, socket

from state import load_state, save_state, reset_state, get_rankings
from ai_helpers import openai_wine_search, openai_label_recognize
from i18n import t, LANGS
from db import get_all_wines, search_wines, add_wine as db_add, delete_wine as db_del, wine_to_session, update_wine as db_upd

st.set_page_config(page_title="La Cata", page_icon="🍷", layout="wide")

# ---- CSS ----
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap');
.stApp{background:#faf7f4!important}
section[data-testid="stSidebar"]{background:#f0ebe6!important;border-right:2px solid #e0d5c8}
h1,h2,h3{font-family:'Playfair Display',serif!important;color:#2c1518!important}
p,li,span,div,label,.stMarkdown,td,th{font-family:'Source Sans 3',sans-serif!important;color:#3a302a!important}
.stButton>button{background:#8b2e38!important;color:#fff!important;border:none!important;border-radius:8px!important;font-weight:600!important}
.stButton>button:hover{background:#a83a46!important}
.stTabs [data-baseweb="tab"]{background:#f0ebe6;border:1.5px solid #d4c5b5;border-radius:8px 8px 0 0;color:#6b5b50;font-weight:600}
.stTabs [aria-selected="true"]{background:#8b2e38!important;color:#fff!important;border-color:#8b2e38!important}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none}
[data-testid="stMetric"]{background:#fff;border:1.5px solid #e0d5c8;border-radius:10px}
[data-testid="stMetricValue"]{color:#8b2e38!important;font-family:'Playfair Display',serif!important}
input,div[data-baseweb="input"] input,textarea{background:#fff!important;border-color:#d4c5b5!important;color:#2c1518!important}
div[data-baseweb="select"]>div{background:#fff!important;border-color:#d4c5b5!important}
.qr-box{background:#fff;border:2px solid #8b2e38;border-radius:14px;padding:24px;text-align:center;margin:16px 0}
.qr-url{background:#f5f0ea;border:1px solid #d4c5b5;border-radius:6px;padding:8px 14px;font-family:monospace;font-size:0.9rem;word-break:break-all;margin:8px 0}
hr{border-color:#e0d5c8!important}
</style>""", unsafe_allow_html=True)

# ---- Helpers ----
def get_ip():
    try: s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(("8.8.8.8",80));ip=s.getsockname()[0];s.close();return ip
    except: return "localhost"

def gen_qr(url):
    q=qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=8,border=2)
    q.add_data(url);q.make(fit=True);img=q.make_image(fill_color="#8b2e38",back_color="#ffffff")
    buf=io.BytesIO();img.save(buf,format="PNG");return base64.b64encode(buf.getvalue()).decode()

def wmeta(w,L):
    return " · ".join(f for f in [
        f"🍇 {w.get('grape','')}" if w.get('grape') else None,
        f"📍 {w.get('origin','')}" if w.get('origin') else None,
        f"🏷️ {w.get('aging','')}" if w.get('aging') else None,
        f"⭐ {w.get('rating','')}" if w.get('rating') else None,
        f"🔥 {w.get('alcohol','')}%" if w.get('alcohol') else None,
        f"💶 {w.get('price','')}€" if w.get('price') else None,
    ] if f)

def rcard(r,L,hl=None):
    pct=round(r["total"]/r["max_total"]*100) if r["max_total"]>0 else 0
    col="#2a7a2a" if pct>=70 else "#9a6b20" if pct>=40 else "#9a3535"
    isme=r["participant"]==hl
    bdr="border:2px solid #8b2e38;background:#fdf8f5;" if isme else "border:1.5px solid #e0d5c8;"
    mbg={"1":"#c9a96e","2":"#a0a0a0","3":"#b07840"}.get(str(r["rank"]),"#e8e0d6")
    mfg="#fff" if r["rank"]<=3 else "#7a6b5e"
    gld="border-color:#c9a96e;background:linear-gradient(135deg,#fffdf5,#fff8ee);" if r["rank"]==1 else ""
    dtl=""
    if isme and r["per_wine"]:
        pts=[f"#{pw['wine_index']+1}:{pw['score']['total']}" for pw in r["per_wine"]]
        dtl=f"<div style='font-size:0.8rem;color:#7a6b5e'>{' · '.join(pts)}</div>"
    yt=f" {t('you',L)}" if isme else ""
    st.markdown(f"""<div style="display:flex;align-items:center;gap:14px;background:#fff;{bdr}{gld}border-radius:10px;padding:12px 18px;margin-bottom:8px">
        <div style="width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;background:{mbg};color:{mfg};font-family:'Playfair Display',serif">{r['rank']}</div>
        <div style="flex:1"><b>{r['participant']}{yt}</b>{dtl}</div>
        <div style="text-align:right"><div style="font-size:1.5rem;font-weight:700;color:{col};font-family:'Playfair Display',serif">{r['total']}</div>
        <div style="font-size:0.7rem;color:#7a6b5e">{t('of',L)} {r['max_total']}</div></div></div>""", unsafe_allow_html=True)

def save_wine_to_db(w):
    """Save a wine to the database, return the db_id."""
    return db_add(w)

def wine_form(prefix, L, opts, defaults=None):
    """Reusable wine form. Returns dict with values."""
    d = defaults or {}
    c1,c2=st.columns(2)
    with c1:
        n=st.text_input(t("f_name",L),value=d.get("name",""),key=f"{prefix}_n")
        cur_g=[g.strip() for g in (d.get("grape","") or "").split(",") if g.strip()]
        g=st.multiselect(t("f_grape",L),opts["grapes"],default=[x for x in cur_g if x in opts["grapes"]],key=f"{prefix}_g")
        o=st.selectbox(t("f_origin",L),[""]+opts["origins"],index=([""]+opts["origins"]).index(d.get("origin","")) if d.get("origin","") in opts["origins"] else 0,key=f"{prefix}_o")
        ag=st.selectbox(t("f_aging",L),[""]+opts["agings"],index=([""]+opts["agings"]).index(d.get("aging","")) if d.get("aging","") in opts["agings"] else 0,key=f"{prefix}_ag")
    with c2:
        rt=st.number_input(t("f_rating",L),0.0,5.0,float(d.get("rating",0) or 0),0.1,key=f"{prefix}_rt")
        al=st.number_input(t("f_alcohol",L),0.0,20.0,float(d.get("alcohol",13) or 13),0.5,key=f"{prefix}_al")
        pr=st.number_input(t("f_price",L),0.0,500.0,float(d.get("price",0) or 0),0.5,key=f"{prefix}_pr")
        types=["","Tinto","Blanco","Rosado","Espumoso","Dulce","Generoso"]
        tp=st.selectbox(t("f_type",L),types,index=types.index(d.get("type","")) if d.get("type","") in types else 0,key=f"{prefix}_tp")
        yr=st.text_input(t("f_year",L),value=d.get("year",""),key=f"{prefix}_yr")
    desc=st.text_area(t("f_description",L),value=d.get("description",""),key=f"{prefix}_desc",placeholder=t("f_description_placeholder",L),height=80)
    return {"name":n,"grape":", ".join(g),"origin":o,"aging":ag,"rating":str(rt) if rt else "","alcohol":str(al),"price":str(pr) if pr else "","type":tp,"year":yr.strip(),"description":desc}

# ---- Init ----
if "openai_key" not in st.session_state: st.session_state.openai_key=""
if "my_name" not in st.session_state: st.session_state.my_name=None

S=load_state(); L=S.get("lang","es"); modo=st.query_params.get("modo","organizador")
is_p=(modo=="participante"); opts=S["options"]

# ============================================================
#                    PARTICIPANT MODE
# ============================================================
if is_p:
    st.markdown(f'<div style="text-align:center"><h1>{t("app_title",L)}</h1><p style="color:#7a6b5e!important;font-style:italic">{t("participant",L)}</p></div>', unsafe_allow_html=True)
    if not S["started"]:
        st.info(f'{t("not_started",L)} {t("wait_organizer",L)}')
        if st.button(t("refresh",L)): st.rerun()
        st.stop()
    if not st.session_state.my_name:
        st.markdown(f"## {t('who_are_you',L)}")
        for p in S["participants"]:
            if st.button(p,key=f"s_{p}",use_container_width=True): st.session_state.my_name=p; st.rerun()
        st.stop()
    me=st.session_state.my_name
    if me not in S["participants"]: st.session_state.my_name=None; st.rerun()
    ch,cb=st.columns([4,1])
    with ch: st.markdown(f"## 🍷 {t('hello',L)}, **{me}**")
    with cb:
        if st.button(t("change",L)): st.session_state.my_name=None; st.rerun()

    nw=len(S["wines"]); done=sum(1 for i in range(nw) if f"{me}_{i}" in S["guesses"])
    st.progress(done/nw if nw else 0, text=f"{done}/{nw} {t('completed',L)}")

    for i,w in enumerate(S["wines"]):
        ky=f"{me}_{i}"; dn=ky in S["guesses"]; rv=i in S["revealed"]
        lbl=f"{'✅' if dn else '📝'} Vino #{i+1}"
        if w.get("type"): lbl+=f" ({w['type']})"
        if dn: lbl+=f" — {t('sent',L)}"
        with st.expander(lbl, expanded=not dn and not rv):
            if dn:
                st.success(t("prediction_sent",L))
                if rv:
                    ranks=get_rankings(S)
                    my_r=next((r for r in ranks if r["participant"]==me),None)
                    if my_r:
                        pw=next((x for x in my_r["per_wine"] if x["wine_index"]==i),None)
                        if pw:
                            st.markdown(f"**{pw['score']['total']} pts**")
                            cols=st.columns(6)
                            flds=[("grape",25),("origin",25),("aging",20),("rating",10),("alcohol",10),("price",10)]
                            for j,(fk,mx) in enumerate(flds):
                                with cols[j]:
                                    pts=pw["score"]["breakdown"].get(fk,0)
                                    ic="🟢" if pts==mx else "🟡" if pts>0 else "🔴"
                                    st.markdown(f"{ic} **{t('score_'+fk,L)}**")
                                    st.markdown(f"Tú: {pw['guess'].get(fk,'—')}")
                                    st.markdown(f"Real: {w.get(fk,'—')}")
                                    st.markdown(f"**+{pts}**")
            else:
                c1,c2=st.columns(2)
                with c1:
                    gg=st.multiselect(t("f_grape",L),opts["grapes"],key=f"pg_{i}")
                    go=st.selectbox(t("f_origin",L),[""]+opts["origins"],key=f"po_{i}")
                    ga=st.selectbox(t("f_aging",L),[""]+opts["agings"],key=f"pa_{i}")
                with c2:
                    gr=st.slider(t("f_rating",L),0.0,5.0,2.5,0.5,key=f"pr_{i}")
                    galc=st.number_input(t("f_alcohol",L),0.0,20.0,13.0,0.5,key=f"pal_{i}")
                    gpr=st.number_input(t("f_price",L),0.0,500.0,10.0,1.0,key=f"pp_{i}")
                if st.button(t("send_prediction",L),key=f"sub_{i}",use_container_width=True):
                    S=load_state(); ck=f"{me}_{i}"
                    if ck in S["guesses"]: st.warning(t("already_sent",L))
                    else:
                        S["guesses"][ck]={"grape":", ".join(gg),"origin":go,"aging":ga,"rating":str(gr),"alcohol":str(galc),"price":str(gpr)}
                        save_state(S); st.success(t("sent_ok",L)); st.rerun()

    if S["revealed"]:
        st.divider()
        st.markdown(f"## {t('partial_ranking',L)} ({len(S['revealed'])}/{nw})")
        for r in get_rankings(S): rcard(r,L,me)
    st.divider()
    if st.button(t("refresh",L),use_container_width=True): st.rerun()
    st.stop()

# ============================================================
#                    ORGANIZER MODE
# ============================================================
with st.sidebar:
    st.markdown(f"# 🍷 {t('organizer',L)}")
    lang_sel=st.selectbox(t("language",L),list(LANGS.keys()),format_func=lambda x:LANGS[x],index=list(LANGS.keys()).index(L))
    if lang_sel!=L: S["lang"]=lang_sel; save_state(S); st.rerun()
    L=lang_sel
    st.divider()
    c1,c2=st.columns(2)
    c1.metric(t("wines",L),len(S["wines"])); c2.metric(t("participants_label",L),len(S["participants"]))
    c1.metric(t("predictions",L),len(S["guesses"])); c2.metric(t("revealed_count",L),f"{len(S['revealed'])}/{len(S['wines'])}")
    st.divider()
    k=st.text_input(t("openai_key",L),value=st.session_state.openai_key,type="password",placeholder="sk-...",label_visibility="collapsed")
    if k!=st.session_state.openai_key: st.session_state.openai_key=k
    if st.session_state.openai_key: st.success(t("key_ok",L))
    else: st.info(t("key_needed",L))
    st.divider()
    all_db=get_all_wines()
    st.caption(f"📚 {len(all_db)} {t('db_wine_count',L)}")
    if st.button(t("reset_session",L),use_container_width=True): reset_state(); st.rerun()

st.markdown(f'<div style="text-align:center"><h1>{t("app_title",L)} — {t("organizer",L)}</h1></div>', unsafe_allow_html=True)

wines=S["wines"]; participants=S["participants"]; guesses=S["guesses"]; revealed=S["revealed"]; started=S["started"]

tab_w,tab_p,tab_c,tab_r,tab_db,tab_o,tab_ab=st.tabs([t("tab_wines",L),t("tab_participants",L),t("tab_control",L),t("tab_results",L),t("tab_db",L),t("tab_options",L),t("tab_about",L)])

# ============================================================
# TAB: WINES
# ============================================================
with tab_w:
    st.markdown(f"## {t('add_wine',L)}")
    method=st.radio("m",[t("method_db",L),t("method_ai",L),t("method_photo",L),t("method_manual",L)],horizontal=True,label_visibility="collapsed")

    # ---- DATABASE ----
    if method==t("method_db",L):
        st.caption(t("db_caption",L))
        dbq=st.text_input("🔍",placeholder=t("db_search",L),label_visibility="collapsed",key="dbq")
        db_wines=search_wines(dbq) if dbq else get_all_wines()
        if not db_wines:
            st.info(t("db_empty",L) if not dbq else t("db_no_results",L))
        else:
            for dw in db_wines:
                c1,c2=st.columns([5,1])
                with c1:
                    desc_preview = f" · *{dw['description'][:60]}...*" if dw.get('description','') and len(dw.get('description',''))>60 else (f" · *{dw['description']}*" if dw.get('description','') else "")
                    st.markdown(f"**{dw['name']}** — {wmeta(dw,L)}{desc_preview}")
                with c2:
                    if st.button(t("db_add_to_tasting",L),key=f"dba_{dw['id']}"):
                        S=load_state()
                        S["wines"].append(wine_to_session(dw))
                        save_state(S); st.rerun()

    # ---- AI SEARCH ----
    elif method==t("method_ai",L):
        st.caption(t("ai_caption",L))
        c1,c2=st.columns([5,1])
        with c1: q=st.text_input("q",placeholder=t("search_placeholder",L),label_visibility="collapsed")
        with c2: sb=st.button("🔍",use_container_width=True)
        if sb and q:
            if not st.session_state.openai_key: st.warning(t("key_needed",L))
            else:
                with st.spinner(t("searching_ai",L)):
                    r=openai_wine_search(q,st.session_state.openai_key)
                if r.get("error"): st.error(r["error"])
                else: st.session_state["_ai"]=r; st.rerun()

    # ---- PHOTO ----
    elif method==t("method_photo",L):
        if not st.session_state.openai_key: st.warning(t("key_needed",L))
        else:
            st.caption(t("photo_caption",L))
            up=st.file_uploader(t("analyze_label",L),type=["jpg","jpeg","png","webp"])
            if up:
                st.image(up,width=250)
                if st.button(t("analyze_label",L)):
                    with st.spinner(t("analyzing",L)):
                        r=openai_label_recognize(up.getvalue(),st.session_state.openai_key)
                    if r.get("error"): st.error(r["error"])
                    else: st.session_state["_ai"]=r; st.rerun()

    # ---- MANUAL ----
    elif method==t("method_manual",L):
        st.info(t("manual_caption",L))
        mw=wine_form("man",L,opts)
        if st.button(t("add_wine_btn",L),use_container_width=True):
            if not mw["name"]: st.error(t("name_required",L))
            else:
                mw["source"]="manual"
                S=load_state(); S["wines"].append(mw); save_state(S)
                db_add(mw)  # Also save to DB
                st.success(t("saved_to_db",L)); st.rerun()

    # ---- Shared AI result form ----
    if st.session_state.get("_ai"):
        st.divider()
        r=st.session_state["_ai"]
        st.success(t("info_found",L))
        if r.get("label_text"): st.info(f"{t('label_read',L)}: **{r['label_text']}**")
        if r.get("description"): st.caption(f"📝 {r['description']}")
        defaults={"name":f"{r.get('name','')} ({r.get('winery','')})".strip(" ()"),"grape":r.get("grape",""),
            "origin":r.get("origin",""),"aging":r.get("aging",""),"rating":r.get("rating",""),
            "alcohol":r.get("alcohol","13"),"price":r.get("price",""),"type":r.get("type",""),"year":r.get("year",""),
            "description":r.get("description","")}
        aw=wine_form("ai",L,opts,defaults)
        bc1,bc2=st.columns(2)
        with bc1:
            if st.button(t("add_this_wine",L),key="add_ai",use_container_width=True):
                aw["source"]=r.get("source","openai")
                S=load_state(); S["wines"].append(aw); save_state(S)
                db_add(aw)  # Also save to DB
                st.session_state["_ai"]=None; st.success(t("saved_to_db",L)); st.rerun()
        with bc2:
            if st.button(t("discard",L),key="dis_ai",use_container_width=True):
                st.session_state["_ai"]=None; st.rerun()

    st.divider()

    # ---- Wine list editable ----
    if wines:
        st.markdown(f"## {t('wines_added',L)}")
        for i,w in enumerate(wines):
            with st.expander(f"**#{i+1}** — {w['name']}  ({wmeta(w,L)})"):
                ew=wine_form(f"e{i}",L,opts,w)
                b1,b2=st.columns(2)
                with b1:
                    if st.button(t("save",L),key=f"sv_{i}",use_container_width=True):
                        S=load_state(); S["wines"][i].update(ew); save_state(S)
                        if w.get("db_id"): db_upd(w["db_id"],ew)
                        st.rerun()
                with b2:
                    if st.button(t("delete",L),key=f"dl_{i}",use_container_width=True):
                        S=load_state(); S["wines"].pop(i)
                        ng={}
                        for k,v in S["guesses"].items():
                            parts=k.rsplit("_",1)
                            if len(parts)==2:
                                o=int(parts[1])
                                if o<i:ng[k]=v
                                elif o>i:ng[f"{parts[0]}_{o-1}"]=v
                        S["guesses"]=ng; S["revealed"]=[r if r<i else r-1 for r in S["revealed"] if r!=i]
                        save_state(S); st.rerun()

# ============================================================
# TAB: DATABASE (Wine Cellar)
# ============================================================
with tab_db:
    st.markdown(f"## {t('db_title',L)}")
    dbq2=st.text_input("🔍",placeholder=t("db_search",L),label_visibility="collapsed",key="dbq2")
    all_w=search_wines(dbq2) if dbq2 else get_all_wines()
    if not all_w:
        st.info(t("db_empty",L) if not dbq2 else t("db_no_results",L))
    else:
        st.caption(f"{len(all_w)} {t('db_wine_count',L)}")
        for dw in all_w:
            with st.expander(f"**{dw['name']}** — {wmeta(dw,L)}"):
                ew=wine_form(f"db{dw['id']}",L,opts,dw)
                b1,b2=st.columns(2)
                with b1:
                    if st.button(t("save",L),key=f"dbsv_{dw['id']}",use_container_width=True):
                        db_upd(dw['id'],ew); st.success(t("saved",L)); st.rerun()
                with b2:
                    if st.button(t("db_delete",L),key=f"dbdl_{dw['id']}",use_container_width=True):
                        db_del(dw['id']); st.rerun()

# ============================================================
# TAB: PARTICIPANTS
# ============================================================
with tab_p:
    st.markdown(f"## {t('tab_participants',L)}")
    c1,c2=st.columns([4,1])
    with c1: nn=st.text_input("n",placeholder=t("participant_name",L),label_visibility="collapsed",key="np")
    with c2:
        if st.button(t("add_participant",L),key="ap",use_container_width=True):
            n=nn.strip()
            if n:
                S=load_state()
                if n in S["participants"]: st.warning(t("already_exists",L))
                else: S["participants"].append(n); save_state(S); st.rerun()
    for p in participants:
        gc=sum(1 for j in range(len(wines)) if f"{p}_{j}" in guesses)
        c1,c2=st.columns([5,1])
        with c1: st.markdown(f"**{p}** — {gc}/{len(wines)} {t('predictions',L).lower()}")
        with c2:
            if st.button("✕",key=f"dp_{p}"):
                S=load_state(); S["participants"].remove(p)
                S["guesses"]={k:v for k,v in S["guesses"].items() if not k.startswith(f"{p}_")}
                save_state(S); st.rerun()

# ============================================================
# TAB: CONTROL
# ============================================================
with tab_c:
    if not wines or not participants:
        st.info(t("add_wines_participants",L))
    elif not started:
        st.markdown(f"## {t('start_tasting',L)}")
        st.markdown(f"**{len(wines)}** {t('wines',L).lower()} · **{len(participants)}** {t('participants_label',L).lower()}")
        if st.button(t("start_btn",L),use_container_width=True,type="primary"):
            S=load_state();S["started"]=True;save_state(S);st.rerun()
    else:
        ip=get_ip(); port=st.get_option("server.port") or 8501
        url=f"http://{ip}:{port}/?modo=participante"
        qr=gen_qr(url)
        st.markdown(f"""<div class="qr-box"><h3>{t('qr_title',L)}</h3>
            <img src="data:image/png;base64,{qr}" width="220" style="margin:10px auto;display:block;border-radius:8px"/>
            <div class="qr-url">{url}</div>
            <p style="color:#6b5b50!important;font-size:0.92rem">{t('qr_instructions',L)}</p></div>""",unsafe_allow_html=True)
        st.divider()
        st.markdown(f"## {t('reveal_wines',L)}")
        for i,w in enumerate(wines):
            gc=sum(1 for p in participants if f"{p}_{i}" in guesses)
            is_rev=i in revealed; all_done=gc==len(participants)
            c1,c2,c3=st.columns([3,2,1])
            with c1: st.markdown(f"**{'✅' if is_rev else '🍷'} #{i+1}** — {w['name']}")
            with c2: st.markdown(f":{'green' if all_done else 'orange'}[{gc}/{len(participants)}]")
            with c3:
                if is_rev: st.markdown("✅")
                elif st.button(t("reveal",L),key=f"rv_{i}",disabled=not all_done):
                    S=load_state();S["revealed"].append(i);save_state(S);st.rerun()
        if revealed:
            st.divider()
            st.markdown(f"## {t('partial_ranking',L)} ({len(revealed)}/{len(wines)})")
            ranks=get_rankings(S)
            for r in ranks: rcard(r,L)
            if len(revealed)>1:
                st.markdown(f"##### {t('pts_per_wine',L)}")
                td=[]
                for r in ranks:
                    row={"🏅":r["rank"],t("participants_label",L):r["participant"]}
                    for pw in r["per_wine"]: row[f"#{pw['wine_index']+1}"]=pw["score"]["total"]
                    row[t("total",L)]=r["total"]; td.append(row)
                if td: st.dataframe(pd.DataFrame(td),use_container_width=True,hide_index=True)
        st.divider()
        if st.button(t("refresh",L),use_container_width=True): st.rerun()

# ============================================================
# TAB: RESULTS
# ============================================================
with tab_r:
    if not revealed: st.info(t("no_revealed",L))
    else:
        ranks=get_rankings(S)
        if ranks:
            st.markdown(f"## {t('ranking',L)}")
            for r in ranks: rcard(r,L)
            st.divider()
            st.markdown(f"## {t('detail',L)}")
            fl={"grape":t("score_grape",L),"origin":t("score_origin",L),"aging":t("score_aging",L),
                "rating":t("score_rating",L),"alcohol":t("score_alcohol",L),"price":t("score_price",L)}
            for idx in sorted(revealed):
                w=wines[idx]
                st.markdown(f"### Vino #{idx+1} — {w['name']}")
                st.caption(wmeta(w,L))
                rows=[]
                for r in ranks:
                    pw=next((x for x in r["per_wine"] if x["wine_index"]==idx),None)
                    if pw:
                        bd=pw["score"]["breakdown"]
                        row={t("participants_label",L):r["participant"]}
                        for fk,fla in fl.items():
                            row[fla]=f"{pw['guess'].get(fk,'—')} → +{bd.get(fk,0)}"
                        row[t("total",L)]=pw["score"]["total"]; rows.append(row)
                if rows: st.dataframe(pd.DataFrame(rows).sort_values(t("total",L),ascending=False),use_container_width=True,hide_index=True)
                st.markdown("---")

# ============================================================
# TAB: OPTIONS
# ============================================================
with tab_o:
    st.markdown(f"## {t('config_options',L)}")
    for cat,cat_key in [("grapes","grapes_config"),("origins","origins_config"),("agings","aging_config")]:
        st.markdown(f"### {t(cat_key,L)}")
        rm=None
        for j,opt in enumerate(opts[cat]):
            c1,c2=st.columns([6,1])
            with c1: st.markdown(f"• {opt}")
            with c2:
                if st.button("✕",key=f"rm_{cat}_{j}"): rm=j
        if rm is not None:
            S=load_state(); S["options"][cat].pop(rm); save_state(S); st.rerun()
        c1,c2=st.columns([4,1])
        with c1: nv=st.text_input(t("new_option_placeholder",L),key=f"new_{cat}",label_visibility="collapsed",placeholder=t("new_option_placeholder",L))
        with c2:
            if st.button(t("add_option",L),key=f"add_{cat}",use_container_width=True):
                if nv.strip():
                    S=load_state()
                    if nv.strip() not in S["options"][cat]:
                        S["options"][cat].append(nv.strip()); save_state(S); st.rerun()
        st.divider()

# ============================================================
# TAB: ABOUT
# ============================================================
with tab_ab:
    st.markdown("""
<div style="text-align:center;padding:2rem 0">
    <h1 style="font-size:3rem;margin-bottom:0">🍷</h1>
    <h2 style="margin-top:0.5rem">La Cata</h2>
</div>
""", unsafe_allow_html=True)

    about_text = {
        "es": """
**La Cata** es una aplicación para organizar catas de vino a ciegas con puntuación automática.

Cada participante intenta adivinar las características del vino (uva, origen, crianza, 
graduación, precio y puntuación) y la app calcula la puntuación de cada uno en tiempo real.

### ✨ Características

- 🤖 **Búsqueda con IA** — Escribe el nombre de un vino y GPT-4o rellena todos los campos
- 📷 **Reconocimiento de etiqueta** — Sube una foto y la IA identifica el vino
- 📚 **Base de datos** — Los vinos se guardan para futuras catas
- 📊 **Clasificación parcial** — Rankings en vivo después de cada vino revelado
- 📱 **QR para participantes** — Escanear y jugar desde el móvil
- 🌍 **Multiidioma** — Castellano, English, Valencià
- ⚙️ **Opciones configurables** — Uvas, D.O.s y crianzas editables

### 📊 Sistema de puntuación (100 pts/vino)

| Campo | Máx | Criterio |
|-------|-----|----------|
| Uva | 25 | Todas acertadas = 25, proporcional al overlap |
| Origen (D.O.) | 25 | Exacto = 25, parcial = 10 |
| Crianza | 20 | Exacto = 20 |
| Puntuación | 10 | ±0.5 = 10, ±1 = 5 |
| Alcohol | 10 | ±0.5% = 10, ±1% = 6, ±2% = 3 |
| Precio | 10 | ±3€ = 10, ±6€ = 6, ±12€ = 3 |

---

Desarrollada por **Cèsar Ferri** con la ayuda de **Claude** (Anthropic).

*El arte de descubrir el vino* 🍷
""",
        "en": """
**La Cata** is an app for organizing blind wine tastings with automatic scoring.

Each participant tries to guess the wine's characteristics (grape, origin, aging, 
alcohol, price and rating) and the app calculates scores in real time.

### ✨ Features

- 🤖 **AI Search** — Type a wine name and GPT-4o fills all fields
- 📷 **Label recognition** — Upload a photo and AI identifies the wine
- 📚 **Database** — Wines are saved for future tastings
- 📊 **Partial ranking** — Live rankings after each wine reveal
- 📱 **QR for participants** — Scan and play from your phone
- 🌍 **Multilingual** — Castellano, English, Valencià
- ⚙️ **Configurable options** — Grapes, D.O.s and aging types are editable

### 📊 Scoring system (100 pts/wine)

| Field | Max | Criteria |
|-------|-----|----------|
| Grape | 25 | All correct = 25, proportional to overlap |
| Origin (D.O.) | 25 | Exact = 25, partial = 10 |
| Aging | 20 | Exact = 20 |
| Rating | 10 | ±0.5 = 10, ±1 = 5 |
| Alcohol | 10 | ±0.5% = 10, ±1% = 6, ±2% = 3 |
| Price | 10 | ±3€ = 10, ±6€ = 6, ±12€ = 3 |

---

Developed by **Cèsar Ferri** with the help of **Claude** (Anthropic).

*The art of discovering wine* 🍷
""",
        "va": """
**La Tast** és una aplicació per a organitzar tasts de vi a cegues amb puntuació automàtica.

Cada participant intenta endevinar les característiques del vi (raïm, origen, criança, 
graduació, preu i puntuació) i l'app calcula la puntuació de cadascú en temps real.

### ✨ Característiques

- 🤖 **Cerca amb IA** — Escriu el nom d'un vi i GPT-4o omple tots els camps
- 📷 **Reconeixement d'etiqueta** — Puja una foto i la IA identifica el vi
- 📚 **Base de dades** — Els vins es guarden per a futures tasts
- 📊 **Classificació parcial** — Rànquings en viu després de cada vi revelat
- 📱 **QR per a participants** — Escanejar i jugar des del mòbil
- 🌍 **Multiidioma** — Castellano, English, Valencià
- ⚙️ **Opcions configurables** — Raïms, D.O.s i criançes editables

### 📊 Sistema de puntuació (100 pts/vi)

| Camp | Màx | Criteri |
|------|-----|---------|
| Raïm | 25 | Totes encertades = 25, proporcional |
| Origen (D.O.) | 25 | Exacte = 25, parcial = 10 |
| Criança | 20 | Exacte = 20 |
| Puntuació | 10 | ±0.5 = 10, ±1 = 5 |
| Alcohol | 10 | ±0.5% = 10, ±1% = 6, ±2% = 3 |
| Preu | 10 | ±3€ = 10, ±6€ = 6, ±12€ = 3 |

---

Desenvolupada per **Cèsar Ferri** amb l'ajuda de **Claude** (Anthropic).

*L'art de descobrir el vi* 🍷
""",
    }
    st.markdown(about_text.get(L, about_text["es"]))

st.markdown(f'<div style="text-align:center;padding:1rem 0;color:#c4b5a5;font-style:italic;font-size:0.82rem;border-top:1px solid #e0d5c8;margin-top:2rem">{t("footer",L)}</div>',unsafe_allow_html=True)
