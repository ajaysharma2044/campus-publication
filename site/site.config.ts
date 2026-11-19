/* EduExplained site configuration (the Astro build). Everything an owner may change without touching a template lives here.
   OWNER: the entries marked OWNER are placeholders that need a real value before a production deploy. */

export type AdProvider = 'none' | 'adsense' | 'other';

export interface School {
  id: string;        // content/articles frontmatter `school`
  slug: string;      // URL segment: /{slug}/
  name: string;      // "Cornell University"
  short: string;     // "Cornell", used in H1s ("Cornell Housing: Every Guide")
  town: string;
  dek: string;       // the school hub's one-paragraph dek, written for that school
}

export interface Topic { id: string; label: string; blurb: string; hidden?: boolean }   // hidden: fewer than 5 published articles (docs/v5 Phase 7b): built and linkable, but out of the navigation, the school hub and the sitemap

export interface AudienceStage { name: string; match: RegExp[]; topics?: string[] }
export interface Audience { id: string; label: string; stages: AudienceStage[] }

export interface Author {
  slug: string;
  name: string;
  kind: 'organization' | 'person';
  role: string;
  bio: string;      // editorial process and expertise
  avatar?: string;  // path under /public
}

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import yaml from 'js-yaml';

/* Google Analytics 4: the measurement id comes from GA4_MEASUREMENT_ID in the environment, else from config/monetization.yml
   (analytics.ga4_measurement_id, the one place both renderers read). Analytics loads only on a production build
   (SITE_PRODUCTION=1) or when SITE_ANALYTICS_PREVIEW=1 is set for an instrumentation check; never in `astro dev`. */
function ga4FromConfig(): string {
  // Vite bundles this file, so import.meta.url is not reliable: look for config/monetization.yml from the build's working
  // directory (site/) upward, then from this file's directory.
  const starts = [process.cwd(), dirname(fileURLToPath(import.meta.url))];
  for (const start of starts) {
    let dir = start;
    for (let i = 0; i < 4; i++) {
      try {
        const doc = yaml.load(readFileSync(resolve(dir, 'config/monetization.yml'), 'utf8')) as any;
        return String(doc?.analytics?.google_tag_id || doc?.analytics?.ga4_measurement_id || '').trim();
      } catch { dir = resolve(dir, '..'); }
    }
  }
  return '';
}
const ga4Id = (process.env.GOOGLE_TAG_ID ?? process.env.GA4_MEASUREMENT_ID ?? '').trim() || ga4FromConfig();
const TAG_RE = /^(G-[A-Z0-9]{6,12}|GTM-[A-Z0-9]{6,10})$/;

export const site = {
  name: 'EduExplained',
  tagline: 'Research-first guides for students, parents and alumni',
  // The production domain is www.eduexplained.com (confirmed by Ajay, 2026-11-11); config/monetization.yml carries it too.
  url: process.env.SITE_URL ?? 'https://www.eduexplained.com',
  production: process.env.SITE_PRODUCTION === '1',   // the live domain build (canonical URLs, ads); indexing is governed by `launched` and each page's index field
  // docs/v5 Phase 9: one flag. false (today): robots.txt is Disallow: /, every page is noindex, follow, the sitemap is empty.
  // true: robots.txt follows config/crawlers.yml, pages with frontmatter index: true are index, follow and fill the sitemap; all others stay noindex, follow.
  launched: process.env.LAUNCHED === 'true',
  language: 'en-US',
  organization: {
    legalName: 'EduExplained',                 // OWNER: legal entity (content/pages/about.md carries the same placeholder)
    sameAs: [] as string[],
  },
  analytics: {
    ga4MeasurementId: TAG_RE.test(ga4Id) ? ga4Id : '',   // 'G-…' (gtag) or 'GTM-…' (Tag Manager container; the GA4 tag is configured inside GTM)
    isGtm: ga4Id.startsWith('GTM-'),
    // true on the live build; SITE_ANALYTICS_PREVIEW=1 turns it on for a preview build so the events can be checked offline
    enabled: TAG_RE.test(ga4Id) && (process.env.SITE_PRODUCTION === '1' || process.env.SITE_ANALYTICS_PREVIEW === '1'),
    environment: process.env.SITE_PRODUCTION === '1' ? 'production' : 'preview',
  },
  ads: {
    // provider: which network renders the fixed units (AdSlot); 'none' keeps them as empty reserved space.
    // adsenseClient: the AdSense publisher id (Ajay, 2026-11-11). When set, every page of every build, the noindex preview
    // included (Ajay: the whole site), loads the AdSense script in its head (site verification and Auto ads) and /ads.txt
    // carries Google's line, whatever the provider; only the dev server leaves it out. The fixed units need provider
    // 'adsense' and a slot id per position.
    provider: 'adsense' as AdProvider,
    adsenseClient: 'ca-pub-7711546311538806',
    slots: { sidebar: '1818144319', leaderboard: '6415864871', inContent: '3789701539', anchor: '' },   // AdSense display units created 2026-11-16; anchor stays empty (no fixed-position unit of our own)
  },
  newsletter: {
    // Placeholder endpoint: the NewsletterSignup form posts here. OWNER: replace with the list provider's endpoint.
    endpoint: '/newsletter/subscribe/',
    method: 'post',
  },
  content: {
    // The Python renderer publishes only articles whose queue row is `published`. The Astro build renders every article in
    // content/articles by default so templates can be reviewed on real pages; set false to mirror the renderer's rule.
    includeUnpublished: process.env.SITE_INCLUDE_UNPUBLISHED === '1',   // SITE_INCLUDE_UNPUBLISHED=1 renders every article (template review only)
    pillarMinWords: 1200,   // a v2 page without page_type renders as a pillar at or above this count, else as a quick answer
  },
  schools: [
    {
      id: 'cornell-university', slug: 'cornell', name: 'Cornell University', short: 'Cornell', town: 'Ithaca',
      dek: 'How Cornell actually works, from housing lotteries and meal-plan math to add/drop deadlines and the bus to New York. Every price, date and rule links to the official page it came from, and the student side of the story is attributed to where we read it.',
    },
  ] as School[],
  topics: [
    { id: 'housing', label: 'Housing', blurb: 'Dorms, program houses, co-ops, Collegetown and downtown apartments, leases, landlords, roommates and moving.' },
    { id: 'getting-around', label: 'Getting around', blurb: 'Flights into ITH and SYR, buses to NYC and Boston, airport rides, TCAT, parking, biking and break travel.' },
    { id: 'money', label: 'Money', blurb: 'Real cost of living, meal plan math, cheap groceries, jobs, financial aid appeals and budgets by scenario.' },
    { id: 'dining', label: 'Dining', blurb: 'Dining halls, meal plans and Big Red Bucks, late-night options, dietary needs, restaurants, groceries and cooking.' },
    { id: 'academics', hidden: true, label: 'Academics', blurb: 'Courses and professors, requirements, registration strategy, add/drop, internal transfer and study spots.' },
    { id: 'transfer', label: 'Transfer', blurb: 'Applying as a transfer, credit evaluation, housing and the residential requirement, orientation and aid.' },
    { id: 'careers', hidden: true, label: 'Careers', blurb: 'Internships, recruiting timelines, career fairs and the employers that hire from campus.' },
    { id: 'parents', hidden: true, label: 'Parents', blurb: 'Visiting, hotels, move-in weekend, graduation and what to send.' },
    { id: 'health-safety', label: 'Health and safety', blurb: 'Cornell Health services and costs, the student health plan and waivers, pharmacies, mental health services, urgent care, and campus and Collegetown safety, fire rules and crime statistics.' },
    { id: 'daily-life', label: 'Daily life', blurb: 'Gyms, health care, phones and banking, winter gear, safety and clubs.' },
    { id: 'alumni', hidden: true, label: 'Alumni', blurb: 'Benefits, events and staying in Ithaca after graduation.' },
  ] as Topic[],
  // The homepage topic rows, in order (spec: Housing, Money, Academics, Careers, Parents).
  homeTopics: ['housing', 'money', 'academics', 'careers', 'parents'],
  // Audience hubs replace the topic hub at /{school}/parents/, /transfer/ and /alumni/: same guides, grouped by journey stage.
  audiences: [
    {
      id: 'parents', label: 'Parents',
      stages: [
        { name: 'Before move-in', match: [/move-in|care package|what to send|pack|bring|dorm|housing/i] },
        { name: 'Paying for it', match: [/cost|budget|spending money|aid|tuition|bursar|pay|insurance|meal plan|bank/i] },
        { name: 'Visiting', match: [/visit|hotel|weekend|graduation|getting to|airport|bus|drive|flight/i] },
        { name: 'Staying in touch', match: [/proxy|emergency|call|health|probation|grades|transcript/i] },
      ],
    },
    {
      id: 'transfer', label: 'Transfer students',
      stages: [
        { name: 'Getting in', match: [/apply|application|admission|guaranteed transfer|transfer option/i] },
        { name: 'Credits and classes', match: [/credit|class|course|enroll|requirement|transfer colleges|internal transfer/i] },
        { name: 'Housing', match: [/housing|dorm|sublet|apartment|where to live|landlord/i] },
        { name: 'Settling in', match: [/orientation|budget|cost|jobs|bank|groceries|bus|bike|study/i] },
      ],
    },
    {
      id: 'alumni', label: 'Alumni',
      stages: [
        { name: 'Staying connected', match: [/network|club|email|reunion|homecoming/i] },
        { name: 'Benefits', match: [/benefit|library|gym|fitness|membership|discount/i] },
        { name: 'Coming back to Ithaca', match: [/visit|hotel|getting to|airport|bus|stay(ing)? in ithaca|summer/i] },
        { name: 'Records and giving', match: [/transcript|diploma|giving|donat/i] },
      ],
    },
  ] as Audience[],
  // Standard fact fields per place category (spec template 7). A place page must supply every field of its category.
  placeCategories: {
    dorm: ['Campus area', 'Who lives here', 'Room types', 'Rate per semester', 'Dining nearby', 'Built', 'Capacity'],
    apartment: ['Neighborhood', 'Walk to campus', 'Bedrooms', 'Rent range', 'Utilities included', 'Lease term', 'Management'],
    dining_hall: ['Campus area', 'Meal type', 'Hours', 'Door price', 'Dietary options', 'Seating'],
  } as Record<string, string[]>,
  // No article names a person as its author; bylines resolve to the editorial organization until the owner adds real authors
  // here (kind: 'person', with slug, role and bio). A page may name one with frontmatter `author: <slug>`.
  authors: [
    {
      slug: 'ajay-sharma', name: 'Ajay Sharma', kind: 'person', role: 'Editor-in-chief',
      // OWNER: {{BIO}} placeholders for Ajay to fill (docs/v5 Phase 8); nothing here is a claim he has approved
      bio: 'Ajay Sharma is the editor-in-chief of EduExplained. {{BIO: Cornell transfer student}} {{BIO: public policy at the Brooks School}} Disclosure: Ajay is the founder of a transfer admissions firm, TransferringUp; EduExplained guides are written and edited independently of it and never recommend it. {{BIO: how he edits: official sources first, every number linked, corrections logged}}',
    },
  ] as Author[],
  defaultAuthor: 'ajay-sharma',   // every page carries a real byline (docs/v5 Phase 8); the editors entry stays for the organization page and old links
  // Traffic-driven lists. OWNER: fill from analytics; empty lists fall back to the longest pillar guides, labeled "Start here".
  mostRead: [] as string[],     // page URLs
  featured: [] as string[],     // homepage lead and the three cards beside it
  nav: [
    { label: 'Schools', href: '/#schools' },
    { label: 'Housing', href: '/cornell/housing/' },
    { label: 'Money', href: '/cornell/money/' },
    { label: 'Data', href: '/cornell/data/' },
  ],
  footer: {
    columns: [
      { title: 'EduExplained', links: [
        { label: 'About', href: '/about/' }, { label: 'Editorial standards', href: '/editorial-standards/' },
        { label: 'Sources', href: '/sources/' }, { label: 'Corrections', href: '/corrections/' },
        { label: 'Contact', href: '/contact/' }, { label: 'Privacy', href: '/privacy/' }, { label: 'Advertise', href: '/advertise/' },
      ] },
      { title: 'Cornell', links: [
        { label: 'Student guide', href: '/cornell/' }, { label: 'Housing', href: '/cornell/housing/' }, { label: 'Money', href: '/cornell/money/' },
        { label: 'Getting around', href: '/cornell/getting-around/' }, { label: 'Data and trackers', href: '/cornell/data/' },
      ] },
      { title: 'Readers', links: [
        { label: 'Transfer students', href: '/cornell/transfer/' }, { label: 'Cross-school guides', href: '/guides/' }, { label: 'Authors', href: '/authors/' }, { label: 'Search', href: '/search/' },
      ] },
    ],
    disclaimer: 'EduExplained is an independent publication. It is not affiliated with Cornell University, the City of Ithaca or any landlord, carrier or business named in a guide.',
  },
};

export type SiteConfig = typeof site;
