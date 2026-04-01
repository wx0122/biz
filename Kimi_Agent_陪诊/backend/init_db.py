"""
Initialize database with seed data.
Run: python init_db.py
"""
from app import create_app
from database import db
from models import Admin, Hospital, Escort, ServiceType, TrainingCourse, City
from auth import hash_password

app = create_app()

with app.app_context():
    db.create_all()

    # ── Admin user ────────────────────────────────
    if not Admin.query.first():
        admin = Admin(
            username="admin",
            hashed_password=hash_password("admin123"),
            display_name="System Admin",
        )
        db.session.add(admin)
        print("Created admin user: admin / admin123")

    # ── Service types ─────────────────────────────
    if not ServiceType.query.first():
        for svc in [
            ServiceType(name="普通陪诊", description="基础陪诊服务，包含挂号、排队、取报告", price=128, icon="clipboard"),
            ServiceType(name="全程陪诊", description="全流程陪诊，包含挂号、就诊陪同、取药、报告解读", price=268, icon="heart"),
            ServiceType(name="特殊陪诊", description="针对老人/儿童/术后患者的专业陪护", price=368, icon="shield"),
        ]:
            db.session.add(svc)

    # ── Hospitals ─────────────────────────────────
    if not Hospital.query.first():
        hospitals = [
            Hospital(name="北京协和医院", level="三甲", address="东城区帅府园1号", city="北京市", province="北京市",
                     latitude=39.914, longitude=116.414, image="/images/hospital1.jpg"),
            Hospital(name="北京大学第一医院", level="三甲", address="西城区西什库大街8号", city="北京市", province="北京市",
                     latitude=39.929, longitude=116.383, image="/images/hospital2.jpg"),
            Hospital(name="中日友好医院", level="三甲", address="朝阳区樱花东街2号", city="北京市", province="北京市",
                     latitude=39.988, longitude=116.428, image="/images/hospital3.jpg"),
            Hospital(name="北京儿童医院", level="三甲", address="西城区南礼士路56号", city="北京市", province="北京市",
                     latitude=39.907, longitude=116.347, image="/images/hospital4.webp"),
            Hospital(name="上海瑞金医院", level="三甲", address="黄浦区瑞金二路197号", city="上海市", province="上海市",
                     latitude=31.218, longitude=121.468, image="/images/hospital1.jpg"),
            Hospital(name="复旦大学附属华山医院", level="三甲", address="静安区乌鲁木齐中路12号", city="上海市", province="上海市",
                     latitude=31.220, longitude=121.445, image="/images/hospital2.jpg"),
            Hospital(name="广州中山大学附属第一医院", level="三甲", address="越秀区中山二路58号", city="广州市", province="广东省",
                     latitude=23.132, longitude=113.281, image="/images/hospital3.jpg"),
            Hospital(name="深圳市人民医院", level="三甲", address="罗湖区东门北路1017号", city="深圳市", province="广东省",
                     latitude=22.557, longitude=114.118, image="/images/hospital4.webp"),
        ]
        for h in hospitals:
            db.session.add(h)

    # ── Escorts ───────────────────────────────────
    if not Escort.query.first():
        escorts = [
            Escort(name="李护士", avatar="/images/avatar1.jpg", rating=4.9, service_count=328, tags="专业,耐心,三甲经验", city="北京市"),
            Escort(name="王医助", avatar="/images/avatar2.jpg", rating=4.8, service_count=256, tags="细心,儿科专长", city="北京市"),
            Escort(name="张护师", avatar="/images/avatar3.jpg", rating=4.9, service_count=412, tags="老年护理,急诊经验", city="北京市"),
            Escort(name="刘护士", avatar="/images/avatar4.jpg", rating=4.7, service_count=189, tags="温柔,骨科陪诊", city="北京市"),
            Escort(name="陈护师", avatar="/images/avatar1.jpg", rating=4.9, service_count=305, tags="专业,内科经验", city="上海市"),
            Escort(name="赵医助", avatar="/images/avatar2.jpg", rating=4.8, service_count=221, tags="细心,妇产科", city="上海市"),
            Escort(name="周护士", avatar="/images/avatar3.jpg", rating=4.6, service_count=167, tags="耐心,肿瘤科", city="广州市"),
            Escort(name="吴护师", avatar="/images/avatar4.jpg", rating=4.8, service_count=278, tags="专业,全科", city="深圳市"),
        ]
        for e in escorts:
            db.session.add(e)

    # ── Training courses ──────────────────────────
    if not TrainingCourse.query.first():
        for c in [
            TrainingCourse(name="基础培训班", description="掌握基本陪诊流程、医院导航、患者沟通技巧", duration="7天", price=1980),
            TrainingCourse(name="进阶提升班", description="深入学习各科室陪诊要点、报告解读、应急处理", duration="14天", price=2980),
            TrainingCourse(name="全能精英班", description="全面培训+实习带教+就业推荐，成为专业陪诊师", duration="30天", price=4980),
        ]:
            db.session.add(c)

    # ── Cities ────────────────────────────────────
    if not City.query.first():
        cities = [
            City(name="北京市", province="北京市", code="110000", is_hot=True),
            City(name="上海市", province="上海市", code="310000", is_hot=True),
            City(name="广州市", province="广东省", code="440100", is_hot=True),
            City(name="深圳市", province="广东省", code="440300", is_hot=True),
            City(name="杭州市", province="浙江省", code="330100", is_hot=True),
            City(name="成都市", province="四川省", code="510100", is_hot=True),
            City(name="南京市", province="江苏省", code="320100", is_hot=False),
            City(name="武汉市", province="湖北省", code="420100", is_hot=False),
            City(name="重庆市", province="重庆市", code="500000", is_hot=False),
            City(name="西安市", province="陕西省", code="610100", is_hot=False),
            City(name="长沙市", province="湖南省", code="430100", is_hot=False),
            City(name="天津市", province="天津市", code="120000", is_hot=False),
            City(name="苏州市", province="江苏省", code="320500", is_hot=False),
            City(name="郑州市", province="河南省", code="410100", is_hot=False),
            City(name="合肥市", province="安徽省", code="340100", is_hot=False),
            City(name="济南市", province="山东省", code="370100", is_hot=False),
            City(name="青岛市", province="山东省", code="370200", is_hot=False),
            City(name="大连市", province="辽宁省", code="210200", is_hot=False),
            City(name="沈阳市", province="辽宁省", code="210100", is_hot=False),
            City(name="昆明市", province="云南省", code="530100", is_hot=False),
            City(name="厦门市", province="福建省", code="350200", is_hot=False),
            City(name="福州市", province="福建省", code="350100", is_hot=False),
            City(name="哈尔滨市", province="黑龙江省", code="230100", is_hot=False),
            City(name="长春市", province="吉林省", code="220100", is_hot=False),
            City(name="石家庄市", province="河北省", code="130100", is_hot=False),
            City(name="太原市", province="山西省", code="140100", is_hot=False),
            City(name="南宁市", province="广西壮族自治区", code="450100", is_hot=False),
            City(name="贵阳市", province="贵州省", code="520100", is_hot=False),
            City(name="兰州市", province="甘肃省", code="620100", is_hot=False),
            City(name="海口市", province="海南省", code="460100", is_hot=False),
        ]
        for c in cities:
            db.session.add(c)

    db.session.commit()
    print("Database initialized with seed data!")
    print(f"  Hospitals: {Hospital.query.count()}")
    print(f"  Escorts: {Escort.query.count()}")
    print(f"  Service Types: {ServiceType.query.count()}")
    print(f"  Training Courses: {TrainingCourse.query.count()}")
    print(f"  Cities: {City.query.count()}")
