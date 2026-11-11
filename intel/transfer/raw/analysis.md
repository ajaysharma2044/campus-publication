# Transferring to Cornell: Lane E, original analysis (raw notes)

Lane: analysis. Topic: Transferring to Cornell. Started 2026-11-11. Demand file intel/transfer/raw/demand-questions.md has a header and no rows, so there are no demand rows to align to.

Tool limits: the Common Data Set PDFs, IRP profile PDFs, ILR transfer-guidelines PDF and a Cornell tuition-proration PDF came back as compressed binary and could not be read (no PDF renderer, no Edit/Bash in this session). web.archive.org is blocked for the fetch tool, so no year-over-year deadline comparison from snapshots was possible. Rental listing sites (rentler, apartmentlist) returned 403 or empty pages, so no rent sample was possible (Analysis 6 says so). The Edit tool is not available, so this file is saved by full rewrite at checkpoints.

## A. Official rules (inputs for the analyses)

| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Transfer entry term | Fall only; "considered for the fall semester only" | https://admissions.cornell.edu/apply/transfer-applicants | current cycle | 2026-11-11 |
| Same on international page | Fall only; deadlines March 15 / April 15 | https://admissions.cornell.edu/how-to-apply/transfer-international-applicants | current | 2026-11-11 |
| Same on FAQ | Fall deadline March 15 | https://faq.enrollment.cornell.edu/kb/article/330-when-should-i-apply-to-cornell-as-a-transfer/ | page fetched 2026-11-06 | 2026-11-11 |
| Deadlines | March 15: application, fee or waiver, portfolio/design supplement. April 15: all other materials | https://admissions.cornell.edu/apply/transfer-applicants | current | 2026-11-11 |
| Decisions | Late April through June (admissions page); "rolling basis beginning in April" (FAQ 427). Two wordings, same start | https://admissions.cornell.edu/apply/transfer-applicants ; https://faq.enrollment.cornell.edu/kb/article/427-when-are-transfer-admission-decisions-released/ | current | 2026-11-11 |
| Application fee | $85; waiver via Common App, no documentation | https://admissions.cornell.edu/apply/transfer-applicants | current | 2026-11-11 |
| Who is a transfer | 12+ semester hours after high school (exam credit excluded) or full-time elsewhere; dual-enrollment HS students apply as first-years; bachelor's holders cannot enroll for a second bachelor's | same | current | 2026-11-11 |
| Time at prior school | Two to four semesters completed; first-semester students not eligible | FAQ 330 above | corpus 2026-11-06 | 2026-11-11 |
| Junior-year transfer | Cornell discourages applying after or during the junior year at a four-year school because the 60-credit cap may waste credits; suggests grad study | https://faq.enrollment.cornell.edu/kb/article/323-can-i-transfer-to-cornell-in-my-junior-year-from-another-college/ | corpus 2026-11-06 | 2026-11-11 |
| Tests | SAT/ACT not required or expected | https://faq.enrollment.cornell.edu/kb/article/322-are-standardized-tests-required-for-transfer-applicants/ (listed in corpus, not opened) ; https://admissions.cornell.edu/apply/transfer-applicants (read) | current | 2026-11-11 |
| Essay | 250 to 650 words plus college writing supplement | https://admissions.cornell.edu/apply/transfer-applicants | current | 2026-11-11 |
| What admissions weighs | Essay (program fit), college record, professor recommendations most important; extracurriculars and HS record also read; admitted students "generally" 3.3+ college GPA; no preference by school type; "about a quarter" of transfers from community colleges | https://faq.enrollment.cornell.edu/kb/article/325-does-cornell-prefer-transfer-applicants-from-certain-colleges-or-types-of-colleges/ | corpus 2026-11-06 | 2026-11-11 |
| Engineering transfers | Admitted directly into one major; cannot apply "undecided" or Independent; must stay in the major at least one academic year | https://faq.enrollment.cornell.edu/kb/article/150-as-a-transfer-student-does-it-matter-which-engineering-major-i-apply-to/ | corpus 2026-11-06 | 2026-11-11 |
| Engineering course requirements (FAQ) | Vary by major and class standing; see transfer requirements page and Engineering Handbook | https://faq.enrollment.cornell.edu/kb/article/140-what-are-the-course-requirements-to-apply-as-a-transfer-student-to-the-cornell-duffield-college-of-engineering/ | corpus | 2026-11-11 |
| CALS course requirements (FAQ) | Each major has foundation courses needed completed or in progress at application; holistic review | https://faq.enrollment.cornell.edu/kb/article/101-what-courses-are-required-to-apply-for-transfer-admission-into-cals/ | corpus | 2026-11-11 |
| Brooks School (FAQ) | Wants interest in public/health policy shown through coursework and activities; mix of social science, quantitative, writing-intensive courses | https://faq.enrollment.cornell.edu/kb/article/441-how-can-i-prepare-as-a-prospective-transfer-applicant-to-the-cornell-jeb-e-brooks-school-of-public-policy/ | corpus | 2026-11-11 |
| Required materials | Transfer Common App, HS transcript, all college transcripts, College Report, instructor Academic Evaluation, mid-term report, essay and supplement; resume for AEM and Hotel; portfolio for architecture/art/fashion/landscape; Engineering course description form after admission | https://admissions.cornell.edu/apply/transfer-applicants | current | 2026-11-11 |
| Transfer Option (admissions page) | Students denied as first-years can re-apply as transfers later; page names a Transfer Option application but gives no detail | https://admissions.cornell.edu/resources/transfer-option-instructions | current | 2026-11-11 |
| Credit evaluation (university FAQ) | Each college case by case; syllabi may be requested; most colleges allow up to 60 semester credits; quarter credit about two-thirds of a semester credit; C or better; mostly counted toward distribution or electives | https://faq.enrollment.cornell.edu/kb/article/327-how-are-my-transfer-credits-evaluated/ | corpus 2026-11-06 | 2026-11-11 |
| Credit evaluation (Arts & Sciences) | Tentative evaluation arrives after the student accepts and pays the deposit; course must match a Cornell course in content and rigor (hours, assessments, textbooks); C or higher (P/F ok with written statement of C or better); credit based on full-time semesters elsewhere, max 60; quarter credit = 2/3 semester; only 4+ quarter-credit courses can fill a requirement; no CLEP; transfer GPA not computed into Cornell GPA; 120 credits to graduate, 100 of them A&S credits; departments decide major/minor use | https://as.cornell.edu/registrar/transferring-credits | corpus 2026-11-06 | 2026-11-11 |
| High-school or after-offer college courses (A&S) | Cannot fill college requirements or count toward the 100 A&S credits | same | corpus 2026-11-06 | 2026-11-11 |
| Exam credit from prior school | Credit awarded by another school only for a departmental exam does not transfer; AP/IB credit follows Cornell's own tables, not the old school's | https://faq.enrollment.cornell.edu/kb/article/326-does-the-credit-i-received-by-examination-at-my-previous-college-or-university-transfer/ ; https://faq.enrollment.cornell.edu/kb/article/332-as-a-transfer-student-will-i-automatically-receive-ap-ib-or-a-level-examinations-credit-if-it-was-accepted-at-my-pre/ | corpus | 2026-11-11 |
| Residential requirement | All new transfers live on campus one academic year; spring transfers: incoming spring plus next academic year; not subject if two years of residential experience at prior institution or matriculating as junior/senior; meal plan required in halls | https://scl.cornell.edu/residential-life/housing/campus-housing/new-transfer-undergraduates | corpus 2026-11-06, re-read live 2026-11-11 | 2026-11-11 |
| Housing placement | Upper-level halls (program houses, South, West House System); rooms grouped when possible; transfers who qualify as first-years placed in first-year housing in limited cases | same | same | 2026-11-11 |
| Housing application timing and exact selection process | Not on the transfer page (only an "Apply for Housing" link); the upper-level page gives no transfer selection details and its dates refer to fall 2025 and April 2026 (stale) | https://scl.cornell.edu/residential-life/housing/campus-housing/upperlevel-undergraduate-campus-housing | read 2026-11-11 | 2026-11-11 |
| Transfer meal plan | Automatically enrolled in Unlimited or the House plan depending on hall | https://scl.cornell.edu/families/first-year-families/transferfamilies | read 2026-11-11 | 2026-11-11 |
| Orientation 2026 dates | First-year move-in Aug 17, transfer move-in Aug 18, Family Orientation Aug 18, NSO Aug 18 to 23, 2026; no transfer-specific events listed on that page | https://scl.cornell.edu/get-involved/tatkon-center-new-students/new-student-orientation | Fall 2026 | 2026-11-11 |
| Orientation transfer track | NSO has a specialized transfer program (transfer small groups, social events); no dates | https://scl.cornell.edu/families/first-year-families/transferfamilies | 2026-11-11 | 2026-11-11 |
| Tatkon Center support | Programming for all new students; signature events (Block Party, CU Downtown) in the first six weeks; page lists no transfer-specific events or dates | https://scl.cornell.edu/get-involved/tatkon-center-new-students/new-students-cornell/transfer/orientation/beyond-first-week | 2026-11-11 | 2026-11-11 |
| Tatkon contact and address (search summary, page not opened) | tatkoncenter@cornell.edu, (607) 255-5808; one Cornell page says Robert Purcell Community Center, another South Balch Hall (conflict); not verified | https://scl.cornell.edu/get-involved/tatkon-center-new-students/about-us (search result only) | 2026 | 2026-11-11 |
| Course enrollment steps by college | Nolan: send transcript to registrar, syllabi for core credit; Dyson: advisor meeting in July to review evaluations; Human Ecology: verify major June 8-30; AAP, Brooks, ILR, CALS: emails early to mid-June; Engineering: emails from early June. Page is stale: Nolan transcript deadline shown as June 1, 2024 | https://scl.cornell.edu/get-involved/tatkon-center-new-students/new-students-cornell/transfer/course-enrollment/college-school-links | page written for 2024 | 2026-11-11 |
| Aid deadlines, Fall 2027 US transfers | March 15, 2027 for CSS Profile and FAFSA; submit after October 1, 2026; CSS code 2098, FAFSA code 002711; NY residents also file NYS aid application; aid estimate shortly after admission; official offer tentatively early April | https://finaid.cornell.edu/apply-aid/prospective-students-or-first-time-aid-applicants | Fall 2027 entry | 2026-11-11 |
| CSS fee waiver | Automatic for US families with AGI up to $100,000 | same | same | 2026-11-11 |
| Aid policy | Meets 100% of demonstrated need; domestic need-blind; international need-aware and must apply for aid at admission | https://admissions.cornell.edu/apply/transfer-applicants | current | 2026-11-11 |
| Aid thresholds | Families earning up to $125,000 (typical assets): grants cover tuition; up to $75,000: cover full cost of attendance; nearly 50% of undergrads get grants | https://news.cornell.edu/stories/2026/03/board-trustees-approves-2026-27-budget-parameters | article dated 2026-03-23 | 2026-11-11 |
| EOP / HEOP transfers | Steps: transfer application (ask for fee waiver), Common App, CSS Profile, FAFSA, IDOC financial documents; HEOP Transfer Certification form for AAP, A&S, Engineering, SC Johnson/Nolan; email stateprograms@cornell.edu if applying to CALS, Human Ecology, ILR, Brooks, Dyson; contact oadi@cornell.edu, 607.255.3841 or 607.255.6384; no deadline listed on the page | https://oadi.cornell.edu/node/50 | Fall 2027 applicants submit 2025 financial documents | 2026-11-11 |

## A2. College-by-college transfer rules (inputs for Analysis 2)

| College | Rule | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Arts & Sciences, external transfer | Complete at least 60 credits at Cornell and four semesters in residence in A&S (the same page words the internal-transfer rule as at least four semesters at Cornell and two in A&S); prerequisites for the intended major for junior entry; no deadline listed; contact as-transfer@cornell.edu | https://as.cornell.edu/admissions/transfer ; https://as.cornell.edu/admissions/admissions-requirements-and-process | current | 2026-11-11 |
| Arts & Sciences, Transfer Option | Two semesters or three quarters full-time at a regionally accredited degree-granting school (summer does not count); broad liberal arts and sciences courses; at least 3.5 GPA each semester and no grade below B-; not an offer of admission, cannot be deferred, coursework cannot be pre-approved | same | current | 2026-11-11 |
| A&S, external transfers who want to move colleges | Apply only after two semesters at Cornell; internal transfer strongly discouraged; internal deadline May 1, 2026, major approval forms June 1, 2026, decisions mid-June (past dates) | same | 2025-26 cycle | 2026-11-11 |
| CALS | 2 full-time semesters (or 3 quarters) finished or in progress; 2 semesters = sophomore standing, 4 semesters or an associate degree = junior standing; more than 4 semesters at a four-year school not eligible; fall only; GPA 3.0 minimum (3.5 for Biological Sciences); up to 15 AP credits count; test plus transfer credit capped at 60; letter grade C or better, no pass/fail; Global and Public Health Sciences takes no transfers; AEM applies through Dyson; no residence figure on page; CALS Admissions 607-255-2036 | https://cals.cornell.edu/education/admissions/undergraduate-admissions/transfer-applicants | current | 2026-11-11 |
| Engineering (Duffield) | Four courses finished or in progress or the application is not reviewed: MATH 1910, MATH 1920, PHYS 1112 with PHYS 1110, CHEM 2090 with 2091; C (not C-) in transferred courses; up to 33 credits per year of full-time study elsewhere; no more than 66 total transfer credits including AP/IB/GCE; at least 60 credits at Cornell; courses about 80% similar in scope and rigor; regionally accredited degree-granting schools only (no MOOCs); syllabus plus certified transcript required; entry at second-semester sophomore, first-semester sophomore or first-semester junior standing; fall entrants from 2025 also need two PE courses and the water competency; deadline March 15; no GPA minimum stated | https://www.duffield.cornell.edu/admissions/transfer-applicants/requirements | Fall 2025 and later entrants | 2026-11-11 |
| Brooks School of Public Policy | Prep courses with letter grades: English composition/writing-intensive 6 credits (2 courses), intro microeconomics 3, statistics and/or calculus 3, intro sociology 3; no GPA minimum, 3.5+ with As and B+s in prep courses "increases competitiveness"; up to 60 credits accepted; at least four semesters in residence on the Ithaca campus; no deadline listed, rolling; number admitted not stated | https://publicpolicy.cornell.edu/undergraduate/apply/transfer-applicants/external-transfers/ | current | 2026-11-11 |
| Dyson (search snippet only, page not read) | External transfer applicants should have at least 3.5 GPA; up to 60 credits per Dyson transfer credit policy (PDF not read) | https://dyson.cornell.edu/wp-content/uploads/sites/5/2019/03/Dyson-Transfer-Credit.pdf (search result) | unknown year | 2026-11-11 |
| ILR | Fall 2026 transfer guidelines PDF exists (unreadable) | https://www.ilr.cornell.edu/sites/default/files-d8/2026-02/transfer-guidelines-fa-26-final.pdf | Fall 2026 | 2026-11-11 (not read) |

## B. Prices (inputs for Analysis 1)

| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Tuition, endowed colleges (and non-NY at contract colleges) | $73,946 (up 3.76%) | https://news.cornell.edu/stories/2026/03/board-trustees-approves-2026-27-budget-parameters | 2026-27 | 2026-11-11 |
| Tuition, NY residents at contract colleges | $49,816 (up 3.76%) | same | 2026-27 | 2026-11-11 |
| Tuition 2025-26 | $71,266 endowed (+4.22%); $48,010 NY contract (+4.24%) | https://www.news.cornell.edu/stories/2025/03/board-trustees-approves-2025-26-budget-parameters | 2025-26 | 2026-11-11 |
| Average housing + dining 2026-27 | $21,348 (up 3.76%) | 2026 news story above | 2026-27 | 2026-11-11 |
| Cost-of-attendance page | Billed: tuition, fees $1,024 ($424 activity + $600 Cornell Health), housing $13,744, food $7,604 = $96,318 (endowed, or non-NY contract); NY contract $72,188. Non-billed: books $1,234, personal $2,182 = $3,416. Totals $99,734 and $75,604. Transportation "varies"; student health plan excluded | https://finaid.cornell.edu/cost-attend and https://www.finaid.cornell.edu/cost-to-attend | heading says 2025-26 | 2026-11-11 |
| CONFLICT on year | The cost page heads these figures "2025-26" and shows an empty "2026-27" heading, but tuition $73,946, housing $13,744 (2026-27 double) and food $7,604 (2026-27 Unlimited plan) match the 2026-27 pages above, and 73,946 / 1.0376 = 71,266 (the 2025-26 tuition). I read the table as 2026-27 prices under a stale heading; this is my inference, not Cornell's statement | URLs in this row and the two rows above | 2026-27 | 2026-11-11 |
| Housing rates 2026-27 per year | Super single $16,595; single $15,566; double $13,744; triple/one-room quad $12,644; quad $13,744; townhouse double $15,566 (per semester: $8,298 / $7,783 / $6,872 / $6,322 / $6,872 / $7,783). Includes utilities and internet up to 200 GB/month. Billed August and December; no deposit; contract binding for the whole year | https://scl.cornell.edu/residential-life/housing/housing-details/rates-amenities-licenses/housing-rates | 2026-27 | 2026-11-11 (corpus 2026-11-06) |
| Co-op rates 2026-27 (per semester) | Prospect of Whitby single $4,889-$5,213, double $4,318; 660 Stewart single $5,640, double $4,981; Triphammer single $4,889, double $4,317, triple $3,972; Redbud single $3,949, double $3,487, triple $2,765; 302 Wait single $5,340-$5,693, double $4,715; 308 Wait same; Wari single $5,640-$6,014, double $4,981; Watermargin single $4,889-$5,213, double $4,317 | same | 2026-27 | 2026-11-11 |
| Meal plans 2026-27 (per year) | Unlimited $7,604; House (required for West Campus House System) $7,604; Collegetown $7,056 (112 Edgemoor, Cascadilla, Schuyler, Sheldon Court, 301 College Ave, 104 Mary Ann Wood); Bear Traditional $7,056; Bear Choice $6,150 and Bear Basic $4,978 (pre-Summer-2021 on-campus students and off-campus); Off-Campus Value $1,824.60; Flex 10/500 $1,348; Just Bucks $1,000. Page does not say which plan co-op residents take or address transfers | https://scl.cornell.edu/residential-life/dining/meal-plans-rates/undergraduate-meal-plans | 2026-27 | 2026-11-11 |
| Internal consistency checks | 6,872 x 2 = 13,744 (matches double); 7,783 x 2 = 15,566; 6,322 x 2 = 12,644; 8,298 x 2 = 16,596 vs listed 16,595 (rounding on Cornell's page); 3,802 x 2 = 7,604; 13,744 + 7,604 = 21,348 (matches Cornell's stated average housing + dining); 424 + 600 = 1,024; 73,946 - 71,266 = 2,680 = 3.76% of 71,266; 49,816 - 48,010 = 1,806 = 3.76% of 48,010; Cornell's stated increase range for unaided students, $1,806 to $2,680, matches | computed from rows above | 2026-27 | 2026-11-11 |
| 2027-28 prices | Not yet published; the aid office says rates are confirmed before early April 2027 offers | https://finaid.cornell.edu/apply-aid/prospective-students-or-first-time-aid-applicants | Fall 2027 entry | 2026-11-11 |
| Rental benchmarks | Tompkins County planning page lists housing snapshots (2024 snapshot released Dec 3, 2025) but no rent figures on the page; HUD FY2027 FMR page returned empty; a search summary gave unverified FMR figures from third-party pages that disagree with each other (studio $1,311 vs $1,263; 1BR $1,434 vs $1,466; 2BR $1,664 vs $1,753) so none is recorded as fact | https://www.tompkinscountyny.gov/planning/housing | 2025-2026 | 2026-11-11 |
| One Cornell-run listing board page | 407 College Ave: range $995 to $2,890 across 2 to 4 bedroom units, "Now renting for 2026-2027", many "Call for price", utilities partly included; no posting date | https://offcampus.housing.cornell.edu/city/ithaca-college-ny/listing/407-college-ave-collegetown-s-best-kept-secret-237329 | 2026-27 lease | 2026-11-11 |

## C. Third-party transfer counts (secondary, labeled; official CDS/IRP PDFs unreadable here)

| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| Transfer applicants, admitted | Fall 2023: 6,581 applied, 834 admitted. Fall 2024: 7,218 / 670. Fall 2025: 7,381 / 864. The 2023 row is on the College Transitions page (dated 2025-01-14, no original source cited); the 2024 and 2025 rows came only from a search-result summary of third-party blogs, which I did not open | https://www.collegetransitions.com/blog/cornell-transfer-acceptance-rate-requirements-application-deadlines/ | Fall 2023-2025 | 2026-11-11 |
| Rates per same blog | 2019 13%, 2020 18%, 2021 15.7%, 2022 13.8%, 2023 12.6% | same | those years | 2026-11-11 |
| Enrolled mix per same blog | 14% from community colleges, 85% from four-year schools, one third NY residents; expected Fall 2024 enrollment 556 (sum of its by-college table; CALS 226); source unclear | same | year unspecified / Fall 2024 | 2026-11-11 |
| First-year admit comparison | 2025: 65,612 applied, 5,516 admitted (8.41%); 2024: 67,846 / 5,358 (7.9%); 2023: 71,164 / 5,168 (7.26%); 2022: 67,380 / 5,852 (8.69%); 2021: 51,500 / 5,514 (10.71%); cites Cornell CDS | https://www.koppelmangroup.com/blog/2026/1/2/cornell-admissions-statistics-2025 | 2021-2025 | 2026-11-11 |
| Transfer enrollment from press | 613 transfers enrolled fall 2017, 645 fall 2018 (Cornell Daily Sun quoting enrollment figures); housing applications up 38; students had up to 10 days after acceptance to apply for housing; notified of housing June 22 | https://www.cornellsun.com/article/2018/12/isolated-vulnerable-and-nervous-transfer-students-express-frustration-over-not-being-able-to-live-on-campus | 2017, 2018 | 2026-11-11 |
| Spring 2023 | 72 new transfers enrolled out of 584 applications, per Shawn Felton, Executive Director of Undergraduate Admissions | https://cornellsun.com/2023/01/26/spring-transfers-start-cornell-journey-mid-year-and-prepare-for-challenges-ahead/ | Spring 2023 | 2026-11-11 |
| 2020 claim | "About 500 to 600 transfer students each semester"; a transfer GroupMe had 350+ members (Sun, Dec 8, 2020) | https://cornellsun.com/2020/12/09/lack-of-connection-marks-transition-to-cornell-for-transfers/ | 2020 | 2026-11-11 |
| Where official counts live | CDS PDFs by year (2025-26 down to 1999); IRP fall transfer profile 2021 | https://irp.cornell.edu/common-data-set ; https://irp.cornell.edu/wp-content/uploads/2021/08/Profile2021-Fall-Transfers.pdf ; https://irp.cornell.edu/wp-content/uploads/2026/09/Cornell-Common-Data-Set-2025-26.pdf | various | 2026-11-11 (PDFs unreadable) |

## D. Pathways

| Fact | Value | Source URL | Applies to | Checked |
|---|---|---|---|---|
| TC3 to CALS | Signed Aug 7, 2025: TC3 Sustainable Farming and Food Systems A.A.S. students with 3.0+ GPA and B or better in transfer courses get "priority consideration" for CALS agricultural sciences bachelor's; page does not say guaranteed, lists no credit count or contact | https://cals.cornell.edu/news/2025/08/cornell-cals-and-tc3-establish-transfer-pathway-for-agriculture-students | Aug 2025 | 2026-11-11 |
| SUNY Broome | 2+2 agreements announced March 2017 for CALS Food Science and Food Operations and Management, from SUNY Broome LAAS: Science | https://cals.cornell.edu/news/2017/02/suny-broome-announce-transfer-agreement-cornell | 2017 | 2026-11-11 |
| SUNY Orange (search snippet of a 2014 document) | CALS articulation agreement, 60 credits max; document dated 2014, status unknown | https://sunyorange.edu/transfer/transfer_agreements/agreements/cals_comprehensive_agreement_revised_july_2014.1414435072.txt (not opened) | 2014 | 2026-11-11 |
| Admissions on school type | No preference by prior institution (see A) | FAQ 325 | corpus | 2026-11-11 |
| Search for general guarantee | No official Cornell page found for a general community-college guarantee; a third-party Q&A on a "guaranteed transfer option" not used (user-generated). The "Iowa Private Transfer Guarantee" results are for Cornell College in Iowa, a different school | search 2026-11-11 | n/a | 2026-11-11 |

## E. Conflicts and stale pages (record both URLs)

1. Spring entry: admissions pages say fall only (https://admissions.cornell.edu/apply/transfer-applicants); the housing page still says spring transfers must live on campus (https://scl.cornell.edu/residential-life/housing/campus-housing/new-transfer-undergraduates); the Sun reported 72 spring 2023 transfers (https://cornellsun.com/2023/01/26/spring-transfers-start-cornell-journey-mid-year-and-prepare-for-challenges-ahead/). A search summary of an admissions page said no external spring 2026 applications. Reading: external spring admission existed in 2023 and is not offered now; the housing page was not updated. Inference, not stated by Cornell.
2. Community college share: "about a quarter" (FAQ 325) vs 14% (College Transitions, source not named).
3. GPA: admitted students "generally" 3.3+ (FAQ 325) vs 3.0 minimum for CALS (3.5 Biological Sciences), no minimum stated for Engineering or Brooks, 3.5 for Dyson (snippet); College Transitions says 3.0 / 3.5 / "3.75 competitive" (authors' opinion).
4. Cost page heading year (see B).
5. Transfers per term: "500 to 600 each semester" (Sun 2020) vs 613 (fall 2017) and 645 (fall 2018) (Sun 2018) vs expected 556 (blog, Fall 2024); fall-only admission now.
6. A&S residence wording: "at least 60 credits at Cornell and four semesters in residency in the College" (transfer section) vs "four semesters in residence at Cornell and two in A&S" (internal-transfer section) on https://as.cornell.edu/admissions/admissions-requirements-and-process. Both lead to a four-semester minimum at Cornell.
7. Stale pages: transfer course-enrollment page still shows a June 1, 2024 Nolan deadline; upper-level housing page shows fall 2025 and April 2026 selection dates; Tatkon address differs across pages.
8. Search-summary claim that transfers with under 7 earned credits go to first-year housing could not be tied to an official page (the scl page returned 403 in one fetch); the live transfer page says only that qualifying first-year-standing transfers are placed in first-year residences in limited situations.

## F. ANALYSES

### Analysis 1: Billed cost of the required on-campus year for a transfer, 2026-27 prices
Question: what does the one required year in university housing cost, by room and plan? Method: add official 2026-27 prices (section B). Assumptions: tuition $73,946 (endowed college or non-NY resident) or $49,816 (NY resident at a contract college); fees $1,024; no financial aid; Cornell has not published 2027-28 prices, so a Fall 2027 entrant will pay more (last increase was 3.76%, which is not a forecast).

| Housing | Meal plan | Housing / yr | Food / yr | Endowed or non-NY billed | NY contract billed |
|---|---|---|---|---|---|
| Triple or one-room quad | Unlimited/House | 12,644 | 7,604 | 95,218 | 71,088 |
| Double, South Collegetown hall | Collegetown | 13,744 | 7,056 | 95,770 | 71,640 |
| Double | Unlimited/House | 13,744 | 7,604 | 96,318 | 72,188 |
| Single | Unlimited/House | 15,566 | 7,604 | 98,140 | 74,010 |
| Super single | Unlimited/House | 16,595 | 7,604 | 99,169 | 75,039 |

Calculation, double: 73,946 + 1,024 + 13,744 + 7,604 = 96,318. NY contract: 49,816 + 1,024 + 13,744 + 7,604 = 72,188. Single: 73,946 + 1,024 + 15,566 + 7,604 = 98,140. Super single: 73,946 + 1,024 + 16,595 + 7,604 = 99,169. Triple: 73,946 + 1,024 + 12,644 + 7,604 = 95,218. Collegetown double: 73,946 + 1,024 + 13,744 + 7,056 = 95,770. NY rows subtract 24,130 (73,946 - 49,816) from each endowed row.
Add non-billed books and personal ($3,416): double endowed 99,734 (matches Cornell's table); NY 75,604 (matches).
Spread: super single minus triple = 3,951 per year (99,169 - 95,218), 4.1% of the triple total (3,951 / 95,218 = 0.0415).
Co-op (housing only; the meal arrangement is not stated on the meal plan page): Triphammer double 2 x 4,317 = 8,634; Redbud triple 2 x 2,765 = 5,530; Wari single 2 x 5,640 = 11,280 to 2 x 6,014 = 12,028. Versus double residence hall 13,744, the Triphammer double is 5,110 less (13,744 - 8,634); this excludes food, so it is not a total. Co-op food cost not found.
Who must live on campus: see A (exemption for those with two years of prior residential experience or junior/senior entry). A junior-entry transfer who lives off campus is not on this table; no off-campus rent sample could be read (Analysis 6).
Result: 95,218 to 99,169 billed for endowed/non-NY; 71,088 to 75,039 for NY contract, before aid. Sample size: none (official price list). Caveat: aid can cover much of this (section A thresholds); 2027-28 rates unknown.

### Analysis 2: How many credits are lost, and how many Cornell semesters remain, under a 60-credit cap
Question: for a transfer applicant with X credits earned, what does the cap mean? Method: A&S rules (section A, A2): max 60 transfer credits, 120 to graduate, at least 60 credits and four semesters at Cornell. Assumption (mine): 15 credits per semester at both schools and every credit accepted up to the cap; real evaluations are case by case and "most" colleges use 60 (FAQ 327).

| Credits earned before Cornell | Semesters there (at 15) | Accepted (cap 60) | Lost | Cornell semesters needed (120 - accepted) / 15 | Total semesters in college |
|---|---|---|---|---|---|
| 30 | 2 | 30 | 0 | 6 | 8 |
| 45 | 3 | 45 | 0 | 5 | 8 |
| 60 | 4 | 60 | 0 | 4 | 8 |
| 75 | 5 | 60 | 15 | 4 | 9 |
| 90 | 6 | 60 | 30 | 4 | 10 |
| 105 | 7 | 60 | 45 | 4 | 11 |

Step: 90 earned, accepted min(90,60) = 60, lost 30, remaining 120 - 60 = 60, 60 / 15 = 4 semesters, plus 6 already done = 10 total, 2 more than 8. This is the arithmetic behind Cornell's advice against junior-year transfer (FAQ 323). The four-semester residence floor (A2) means even a 90-credit transfer cannot finish in fewer than 4 Cornell semesters, so the loss is not recoverable by overloading.
Quarter conversion: credits x 2/3. 4 quarter credits = 2.67 semester credits; 5 = 3.33; 180 quarter credits = 120 semester credits; 90 quarter credits = 60 semester credits, hitting the cap exactly. A&S counts only 4+ quarter-credit courses toward requirements.
Extra-year cost, 90-credit case: if it adds two semesters (one year) at 2026-27 endowed tuition and fees: 73,946 + 1,024 = 74,970 before housing and aid. Caveats: estimate from the stated cap; AP/exam credits, summer credits and overload could change it.

Analysis 2b: how the caps differ by college (A2 sources)

| College | Cap on credits | Minimum at Cornell | Notes |
|---|---|---|---|
| A&S | 60 | 60 credits, four semesters | 120 to graduate, 100 must be A&S credits |
| CALS | 60 (test + transfer combined; AP up to 15) | not stated on page | standing by semesters: 2 = sophomore, 4+ = junior |
| Engineering | 66 total, and 33 per full year elsewhere | 60 credits | Engineering counts AP in the 66; it does not stop a two-year student at 66, but a student with 3 years elsewhere is capped by the 66 |
| Brooks | 60 | four semesters, Ithaca | prep courses total 6 + 3 + 3 + 3 = 15 credits |

Engineering example: 2 full years elsewhere x 33 = 66, which equals the total cap; 1.5 years x 33 = 49.5 credits. In other words the cap works out to 33 per year even when the student took more. Whether the engineering degree needs 120 credits was not read, so no semesters-remaining figure is given for it.

### Analysis 3: Transfer admission rates from the third-party counts (arithmetic check; numbers unverified against CDS)
Method: admits / applicants, compared to first-year rates from the Koppelman page (section C).

| Fall | Transfer applicants | Admitted | Admit rate | Applicants per admit | First-year rate |
|---|---|---|---|---|---|
| 2023 | 6,581 | 834 | 834 / 6,581 = 12.67% | 7.89 | 7.26% (5,168 / 71,164) |
| 2024 | 7,218 | 670 | 670 / 7,218 = 9.28% | 10.77 | 7.90% (5,358 / 67,846) |
| 2025 | 7,381 | 864 | 864 / 7,381 = 11.71% | 8.54 | 8.41% (5,516 / 65,612) |

Changes 2023 to 2025: applicants +800 (+12.2%); admits +30 (+3.6%). 2024 vs 2023: admits -164 (-19.7%). Transfer applicants rose while first-year applicants fell 71,164 to 65,612 (-7.8%). Spring 2023: 72 enrolled / 584 applications = 12.3% (enrolled over applications, not an admit rate, so not comparable). Trend in enrollment from press: 613 (fall 2017) to 645 (fall 2018) is +32 (+5.2%). Result: on these figures a transfer applicant's odds were about 1.4 to 1.7 times a first-year applicant's, but the admit rate swung 3.4 points in one year, so no stable "rate" can be quoted. Caveats: 2024 and 2025 rows second-hand; yield (enrolled / admitted) not found; Cornell's own table unreadable here.

### Analysis 4: Student voice, counted across dated pieces (voice only, not fact)
Method: pieces found by search 2026-11-11 and read; one tally per piece per theme the piece itself raises.

| Piece (outlet, author, date) | Housing | Social connection | Credits / graduation timing | Workload / academic adjustment |
|---|---|---|---|---|
| Sun, 2018-12 (news, students quoted) https://www.cornellsun.com/article/2018/12/isolated-vulnerable-and-nervous-transfer-students-express-frustration-over-not-being-able-to-live-on-campus | yes | yes (isolation) | no | no |
| Sun, Kim, 2019-05-02 (essay) https://www.cornellsun.com/article/2019/05/kim-what-it-means-to-be-a-transfer-at-cornell | no | yes | no | yes |
| Sun, 2020-12-08 (news) https://cornellsun.com/2020/12/09/lack-of-connection-marks-transition-to-cornell-for-transfers/ | spread across campus | yes | no | no |
| Sun, 2023-01-26 (news, spring transfers) https://cornellsun.com/2023/01/26/spring-transfers-start-cornell-journey-mid-year-and-prepare-for-challenges-ahead/ | no | yes | yes | yes |
| Sun, Eisenhart, 2025-05-01 (letter) https://www.cornellsun.com/article/2025/05/a-letter-to-incoming-transfer-students-what-no-one-tells-you | dorm-question awkwardness | yes | no | partly (study methods) |
| Human Ecology blog, Silverman, about Oct 2024 https://hecec.human.cornell.edu/?p=8161 | yes (positive, West Campus) | yes (positive) | partly (quarter to semester switch) | yes |
| Her Campus, Hervert and Schwindt, no date (entered fall 2018) https://www.hercampus.com/school/cornell/transfer-option-blessing-disguise/ | no | yes | yes (positive: most classes approved) | no |

Count: social connection 7 of 7 pieces; housing 3 of 7 as a theme (a fourth in passing); credits or graduation timing 2 of 7 (spring 2023 worried; Her Campus reassured), 3 if the quarter-to-semester switch counts; workload or academic adjustment 4 of 7. N = 7, hand-picked from searches, not a random sample; the Sun pieces skew negative (news framing), Cornell-run blogs skew positive. Voice items: Eitan Wolf, 2018, off campus "so isolated"; Will Bodenman '23, 2020, arrived "not knowing a soul" (the Sun's phrasing of his account); Abbey Yang '25, 2023, advisor said biology credits should count but her DUST record did not yet show it; Cynthia Cui '25, 2023, Cornell more rural than UC Santa Barbara. A CollegeVine reply (about "3 years ago") summarizes what "many transfer students have reported" but the poster says they did not transfer, so it is not a transfer account (https://www.collegevine.com/faq/27647/cornell-transfer-experiences). Reddit: a search surfaced only mirror pages; two 2026 commenters (via mirror) said friends were possible; not used. 2018 housing episode: Cornell cited an "unusually large" transfer class and "overwhelming demand"; later arranged traditional rooms.

### Analysis 5: Year-over-year deadline comparison
Not possible in this lane: web.archive.org is blocked, so no dated snapshots were read. Current rules only (section A). Changes visible from live pages: housing page language still says "Spring transfers" while admissions says fall only (conflict 1); residential requirement began for fall 2022 entrants (page wording); Engineering added two PE courses and the water competency for fall 2025 and later entrants (page wording); Fall 2027 aid deadline March 15, 2027 versus the March 15, 2026 deadline a search result gave for Fall 2026 (same date, one year apart).

### Analysis 6: Off-campus rent for junior-entry transfers
Not completed. Attempted: rentler.com listing pages (403 for five addresses), apartmentlist.com (empty page), HUD FY2027 FMR page (empty), Cornell off-campus board (one listing read, range only). Search-result snippets (not read as pages, not a sample, no dates of posting) showed 1-bedroom asking prices for 2027 leases from about $1,450 to $3,000 a month in Collegetown, with some priced per person; I do not present a median. A fact checker could redo this with at least 15 listing pages read one by one.

### Analysis 7: Count of how many college rule pages state each constraint (what a transfer must read per college, N = 6 college pages)
Residence floor stated: A&S yes, Brooks yes, Engineering yes (60 credits), CALS no, Dyson not read, ILR not read = 3 of 4 read. Credit cap stated: A&S, CALS, Engineering, Brooks = 4 of 4 read. GPA minimum stated: CALS yes (3.0 or 3.5), Brooks no (3.5 "increases competitiveness"), Engineering no, A&S no = 1 of 4. Deadline on the college page: Engineering yes (March 15), CALS no, A&S no, Brooks no = 1 of 4. Result: the March 15 date lives on the central page and Engineering; students cannot get a GPA floor from most college pages. Caveat: N is small.

## G. Coverage

Covered (sourced rows): applying as a transfer (deadlines, fee, materials, eligibility, essay, tests, decisions); the Transfer Option (A&S rules, admissions page); credit evaluation and what transfers (university FAQ, A&S, CALS, Engineering, Brooks; quarter conversion; exam credit); residential requirement and housing placement, meal plans, 2026-27 rates; orientation (2026 dates, transfer track); financial aid for transfers (deadlines, forms, EOP/HEOP, thresholds); spring versus fall entry (fall only; conflict recorded); community college pathways (TC3 2025, SUNY Broome 2017, SUNY Orange 2014 snippet); academic adjustment voice (7 pieces); cost of a year.
Thin: Dyson, ILR, Hotel (Nolan), AAP, Human Ecology external transfer rules (PDFs unreadable or pages not found); Cornell's own transfer admit/enroll counts (PDFs unreadable, only third-party figures); transfer enrollment by college and prior institution type; academic-adjustment support (advising offices, DUST, add/drop) beyond the college-links page; international transfer rules (F-1 transfer pages exist in the corpus but were not read in this lane); off-campus rent for exempt juniors; housing application timing for transfers; Reddit/forum voice (mirrors only).
Not found: an official Cornell guaranteed-admission page for community colleges; year-over-year deadline history (archive blocked); a single published average transfer GPA; a published transfer-specific orientation schedule beyond move-in dates; co-op meal arrangement; 2027-28 prices.

## H. Pages read

| # | Page | URL | Date applies | Result |
|---|---|---|---|---|
| 1 | Transfer applicants | https://admissions.cornell.edu/apply/transfer-applicants | current | read |
| 2 | Transfer international applicants | https://admissions.cornell.edu/how-to-apply/transfer-international-applicants | current | read |
| 3 | Transfer option instructions | https://admissions.cornell.edu/resources/transfer-option-instructions | current | read |
| 4 | FAQ 330 | https://faq.enrollment.cornell.edu/kb/article/330-when-should-i-apply-to-cornell-as-a-transfer/ | 2026-11-06 | corpus |
| 5 | FAQ 327 | https://faq.enrollment.cornell.edu/kb/article/327-how-are-my-transfer-credits-evaluated/ | 2026-11-06 | corpus |
| 6 | FAQ 427 | https://faq.enrollment.cornell.edu/kb/article/427-when-are-transfer-admission-decisions-released/ | 2026-11-06 | corpus |
| 7 | FAQ 325 | https://faq.enrollment.cornell.edu/kb/article/325-does-cornell-prefer-transfer-applicants-from-certain-colleges-or-types-of-colleges/ | 2026-11-06 | corpus |
| 8 | FAQ 323 | https://faq.enrollment.cornell.edu/kb/article/323-can-i-transfer-to-cornell-in-my-junior-year-from-another-college/ | 2026-11-06 | corpus |
| 9 | FAQ 326 | https://faq.enrollment.cornell.edu/kb/article/326-does-the-credit-i-received-by-examination-at-my-previous-college-or-university-transfer/ | 2026-11-06 | corpus |
| 10 | FAQ 332 | https://faq.enrollment.cornell.edu/kb/article/332-as-a-transfer-student-will-i-automatically-receive-ap-ib-or-a-level-examinations-credit-if-it-was-accepted-at-my-pre/ | 2026-11-06 | corpus |
| 11 | FAQ 441 | https://faq.enrollment.cornell.edu/kb/article/441-how-can-i-prepare-as-a-prospective-transfer-applicant-to-the-cornell-jeb-e-brooks-school-of-public-policy/ | 2026-11-06 | corpus |
| 12 | FAQ 150 | https://faq.enrollment.cornell.edu/kb/article/150-as-a-transfer-student-does-it-matter-which-engineering-major-i-apply-to/ | 2026-11-06 | corpus |
| 13 | FAQ 140 | https://faq.enrollment.cornell.edu/kb/article/140-what-are-the-course-requirements-to-apply-as-a-transfer-student-to-the-cornell-duffield-college-of-engineering/ | 2026-11-06 | corpus |
| 14 | FAQ 101 | https://faq.enrollment.cornell.edu/kb/article/101-what-courses-are-required-to-apply-for-transfer-admission-into-cals/ | 2026-11-06 | corpus |
| 15 | FAQ section 34 | https://faq.enrollment.cornell.edu/kb/section/34/ | 2026-11-06 | corpus |
| 16 | New transfer undergraduates | https://scl.cornell.edu/residential-life/housing/campus-housing/new-transfer-undergraduates | 2026-11-06 / live | corpus + live |
| 17 | Families of transfer students | https://scl.cornell.edu/families/first-year-families/transferfamilies | 2026 | read |
| 18 | Housing rates | https://scl.cornell.edu/residential-life/housing/housing-details/rates-amenities-licenses/housing-rates | 2026-27 | corpus |
| 19 | Undergraduate meal plans | https://scl.cornell.edu/residential-life/dining/meal-plans-rates/undergraduate-meal-plans | 2026-27 | read |
| 20 | Upper-level housing | https://scl.cornell.edu/residential-life/housing/campus-housing/upperlevel-undergraduate-campus-housing | stale | read |
| 21 | New student orientation | https://scl.cornell.edu/get-involved/tatkon-center-new-students/new-student-orientation | Fall 2026 | read |
| 22 | Beyond the first week | https://scl.cornell.edu/get-involved/tatkon-center-new-students/new-students-cornell/transfer/orientation/beyond-first-week | 2026 | read |
| 23 | Transfer course enrollment, college links | https://scl.cornell.edu/get-involved/tatkon-center-new-students/new-students-cornell/transfer/course-enrollment/college-school-links | 2024 | read |
| 24 | A&S transferring credits | https://as.cornell.edu/registrar/transferring-credits | 2026-11-06 | corpus |
| 25 | A&S admissions requirements | https://as.cornell.edu/admissions/admissions-requirements-and-process | 2026 | read |
| 26 | A&S transfer | https://as.cornell.edu/admissions/transfer | 2026 | read |
| 27 | Cost to attend | https://finaid.cornell.edu/cost-attend | heading 2025-26 | read |
| 28 | Cost to attend (www) | https://www.finaid.cornell.edu/cost-to-attend | heading 2025-26 | read |
| 29 | Aid, prospective transfers | https://finaid.cornell.edu/apply-aid/prospective-students-or-first-time-aid-applicants | Fall 2027 | read |
| 30 | Trustees 2026-27 budget | https://news.cornell.edu/stories/2026/03/board-trustees-approves-2026-27-budget-parameters | 2026-03-23 | read |
| 31 | Trustees 2025-26 budget | https://www.news.cornell.edu/stories/2025/03/board-trustees-approves-2025-26-budget-parameters | 2025-03-27 | read |
| 32 | CALS and TC3 | https://cals.cornell.edu/news/2025/08/cornell-cals-and-tc3-establish-transfer-pathway-for-agriculture-students | 2025-08-07 | read |
| 33 | SUNY Broome | https://cals.cornell.edu/news/2017/02/suny-broome-announce-transfer-agreement-cornell | 2017 | corpus |
| 34 | CALS transfer applicants | https://cals.cornell.edu/education/admissions/undergraduate-admissions/transfer-applicants | current | read |
| 35 | Brooks external transfers | https://publicpolicy.cornell.edu/undergraduate/apply/transfer-applicants/external-transfers/ | current | read |
| 36 | Engineering transfer requirements | https://www.duffield.cornell.edu/admissions/transfer-applicants/requirements | Fall 2025+ | read |
| 37 | EOP/HEOP transfers | https://oadi.cornell.edu/node/50 | Fall 2027 | read |
| 38 | IRP Common Data Set index | https://irp.cornell.edu/common-data-set | 2026 | read (links only) |
| 39 | Tompkins County housing | https://www.tompkinscountyny.gov/planning/housing | 2025 | read |
| 40 | Cornell off-campus listing, 407 College Ave | https://offcampus.housing.cornell.edu/city/ithaca-college-ny/listing/407-college-ave-collegetown-s-best-kept-secret-237329 | 2026-27 | read |
| 41 | College Transitions | https://www.collegetransitions.com/blog/cornell-transfer-acceptance-rate-requirements-application-deadlines/ | 2025-01-14 | read (secondary) |
| 42 | Koppelman Group | https://www.koppelmangroup.com/blog/2026/1/2/cornell-admissions-statistics-2025 | 2026-01-02 | read (secondary) |
| 43 | Sun 2018 | https://www.cornellsun.com/article/2018/12/isolated-vulnerable-and-nervous-transfer-students-express-frustration-over-not-being-able-to-live-on-campus | 2018-12 | read (voice) |
| 44 | Sun Kim 2019 | https://www.cornellsun.com/article/2019/05/kim-what-it-means-to-be-a-transfer-at-cornell | 2019-05-02 | read (voice) |
| 45 | Sun 2020 | https://cornellsun.com/2020/12/09/lack-of-connection-marks-transition-to-cornell-for-transfers/ | 2020-12-08 | read (voice) |
| 46 | Sun 2023 spring transfers | https://cornellsun.com/2023/01/26/spring-transfers-start-cornell-journey-mid-year-and-prepare-for-challenges-ahead/ | 2023-01-26 | read (voice + counts) |
| 47 | Sun Eisenhart 2025 | https://www.cornellsun.com/article/2025/05/a-letter-to-incoming-transfer-students-what-no-one-tells-you | 2025-05-01 | read (voice) |
| 48 | Human Ecology blog | https://hecec.human.cornell.edu/?p=8161 | about 2024 | read (voice) |
| 49 | Her Campus | https://www.hercampus.com/school/cornell/transfer-option-blessing-disguise/ | undated | read (voice) |
| 50 | CollegeVine | https://www.collegevine.com/faq/27647/cornell-transfer-experiences | about 3 years old | read (voice, weak) |

Failed or unreadable: https://irp.cornell.edu/wp-content/uploads/2026/09/Cornell-Common-Data-Set-2025-26.pdf, https://irp.cornell.edu/wp-content/uploads/2025/07/CDS-2024-2025-v6-print.pdf, https://irp.cornell.edu/wp-content/uploads/2021/08/Profile2021-Fall-Transfers.pdf, https://irp.cornell.edu/wp-content/uploads/2024/04/1000156.pdf, https://www.ilr.cornell.edu/sites/default/files-d8/2026-02/transfer-guidelines-fa-26-final.pdf, https://experience.cornell.edu/sites/default/files/resource-files/Proration%20Chart%20for%20Students%20with%20Non%20Cornell%20Credit.pdf (all binary, unreadable); web.archive.org (blocked); rentler.com listings, apartmentlist.com (403 or empty); collegedata.com (502); https://admissions.cornell.edu/community/blog/how-to-succeed-a-transfer-student (403); https://cals.cornell.edu/.../transfer-option-frequently-asked-questions (403); https://business.cornell.edu/.../transfer-option/ (404); https://admissions.cornell.edu/how-to-apply/transfer-applicants/transfer-requirements (404); HUD FY2027 FMR page (empty).

## Lane complete: about 150 facts, 50 sources (plus 6 unreadable PDFs listed), about 8,500 words, 2026-11-11
