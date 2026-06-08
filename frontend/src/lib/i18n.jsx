import React, { createContext, useContext, useState, useCallback } from "react";

// 경량 i18n (외부 패키지 없음).
// - 기본 언어: 영어(기존 동작 보존). 사이드바 토글로 한국어 전환.
// - 선택 언어는 localStorage("ncb_lang")에 저장 → 새로고침해도 유지.
// - 한국어 키가 없으면 영어로, 영어도 없으면 키 문자열 그대로 폴백(화면이 절대 안 깨짐).
// - 기술 약어/CLI 키워드(SNMP, HSRP, VRRP, DNS, IOS-XE 등)는 번역하지 않고 영어 유지.

const STORAGE_KEY = "ncb_lang";
const DEFAULT_LANG = "en";

const DICT = {
  en: {
    // 공통
    "common.retry": "Retry",
    "common.refresh": "Refresh",
    "common.import": "Import",
    "common.importing": "Importing...",
    "common.newConfig": "New Config",
    "common.use": "Use",
    "common.copy": "Copy",
    "common.download": "Download",
    "common.edit": "Edit",
    "common.delete": "Delete",
    "common.duplicate": "Duplicate",
    "common.lock": "Lock",
    "common.unlock": "Unlock",

    // 언어 토글
    "lang.toggle": "한국어",

    // 사이드바
    "nav.dashboard": "Dashboard",
    "nav.newConfig": "New Config",
    "nav.templates": "Templates",
    "sidebar.subtitle": "Cisco IOS-XE Config Tool",

    // 상태 배지(공유)
    "status.draft": "Draft",
    "status.validated": "Validated",
    "status.generated": "Generated",

    // 대시보드
    "dashboard.title": "Dashboard",
    "dashboard.subtitle": "Configuration project overview",
    "dashboard.loading": "Loading dashboard...",
    "dashboard.loadError": "Failed to load dashboard data",
    "dashboard.stat.total": "Total Projects",
    "dashboard.stat.drafts": "Drafts",
    "dashboard.stat.generated": "Generated",
    "dashboard.stat.templates": "Templates",
    "dashboard.recent": "Recent Projects",
    "dashboard.col.name": "Name",
    "dashboard.col.platform": "Platform",
    "dashboard.col.hostname": "Hostname",
    "dashboard.col.status": "Status",
    "dashboard.col.updated": "Updated",
    "dashboard.empty": "No projects yet. Create your first configuration.",
    "dashboard.unnamed": "Unnamed",
    "dashboard.import.success": "Imported \"{name}\"",
    "dashboard.import.fail": "Import failed: {detail}",

    // 템플릿 라이브러리
    "templates.title": "Template Library",
    "templates.subtitle": "Reusable configuration templates by platform",
    "templates.allPlatforms": "All Platforms",
    "templates.loading": "Loading templates...",
    "templates.empty": "No templates found.",
    "templates.emptyHint": "Templates are seeded on first load. Try refreshing.",
    "templates.loadError": "Failed to load templates",
    "templates.duplicated": "Template duplicated",
    "templates.duplicateFail": "Duplicate failed: {detail}",
    "templates.locked": "Template locked",
    "templates.unlocked": "Template unlocked",
    "templates.lockFail": "Lock toggle failed",
    "templates.confirmDelete": "Delete template \"{name}\"?",
    "templates.deleted": "Template deleted",
    "templates.deleteFail": "Delete failed: {detail}",
    "templates.created": "Project created from template",
    "templates.createFail": "Failed to create project from template",

    // 프로젝트 상세
    "pd.loading": "Loading project...",
    "pd.notFound": "Project not found.",
    "pd.loadError": "Failed to load project",
    "pd.unnamed": "Unnamed Project",
    "pd.validate": "Validate",
    "pd.generate": "Generate",
    "pd.validation.errwarn": "Validation: {errors} error(s), {warnings} warning(s)",
    "pd.validation.warnOnly": "Validation passed with {warnings} warning(s)",
    "pd.validation.passed": "Validation passed. Ready to generate.",
    "pd.validation.fail": "Validation failed: {detail}",
    "pd.generate.success": "Configuration generated successfully",
    "pd.generate.fail": "Generation failed: {detail}",
    "pd.export.success": "Exported as {format}",
    "pd.export.fail": "Export failed: {detail}",
    "pd.confirmDelete": "Delete this project? This cannot be undone.",
    "pd.deleted": "Project deleted",
    "pd.deleteFail": "Delete failed",
    "pd.copied": "Copied to clipboard",
    "pd.copyFail": "Copy failed — select and copy the text manually",
    "pd.tab.clean": "Clean Config",
    "pd.tab.annotated": "Annotated",
    "pd.tab.validation": "Validation",
    "pd.tab.checklist": "Checklist",
    "pd.tab.revisions": "Revisions",
    "pd.tab.export": "Export",
    "pd.empty.clean": "No config generated yet. Click 'Generate' to create configuration.",
    "pd.empty.annotated": "No annotated config available. Generate config first.",
    "pd.empty.validation": "No validation results. Click 'Validate' to check your configuration.",
    "pd.empty.checklist": "No checklist available. Generate config first.",
    "pd.errCount": "{n} error(s)",
    "pd.warnCount": "{n} warning(s)",
    "pd.infoCount": "{n} info(s)",
    "pd.export.title": "Export Project",
    "pd.export.txtLabel": "Clean Config (TXT)",
    "pd.export.txtDesc": "CLI commands only, ready for paste",
    "pd.export.jsonLabel": "Project (JSON)",
    "pd.export.jsonDesc": "Full project data with all settings",
    "pd.export.yamlLabel": "Project (YAML)",
    "pd.export.yamlDesc": "Full project data in YAML format",
    "pd.export.future": "DOCX and PDF export will be available in a future release.",
    "pd.rev.count": "{n} revision(s)",
    "pd.rev.empty": "No revisions yet. Updates to this project will be tracked here.",
    "pd.rev.unnamedSnap": "Unnamed snapshot",
    "pd.rev.comparing": "Comparing",
    "pd.rev.revisionAt": "revision {time}",
    "pd.rev.current": "current",
    "pd.rev.selectHint": "Select a revision on the left to see changes.",
    "pd.rev.added": "+{n} added",
    "pd.rev.removed": "-{n} removed",
    "pd.rev.changed": "~{n} changed",
    "pd.rev.noSelected": "No revision selected.",
    "pd.rev.noDiff": "No differences detected between this revision and the current project.",
    "pd.diff.op": "Op",
    "pd.diff.field": "Field",
    "pd.diff.prev": "Previous",
    "pd.diff.current": "Current",
  },

  ko: {
    // 공통
    "common.retry": "다시 시도",
    "common.refresh": "새로고침",
    "common.import": "가져오기",
    "common.importing": "가져오는 중...",
    "common.newConfig": "새 구성",
    "common.use": "사용",
    "common.copy": "복사",
    "common.download": "다운로드",
    "common.edit": "편집",
    "common.delete": "삭제",
    "common.duplicate": "복제",
    "common.lock": "잠금",
    "common.unlock": "잠금 해제",

    // 언어 토글
    "lang.toggle": "English",

    // 사이드바
    "nav.dashboard": "대시보드",
    "nav.newConfig": "새 구성",
    "nav.templates": "템플릿",
    "sidebar.subtitle": "Cisco IOS-XE 설정 도구",

    // 상태 배지(공유)
    "status.draft": "초안",
    "status.validated": "검증됨",
    "status.generated": "생성됨",

    // 대시보드
    "dashboard.title": "대시보드",
    "dashboard.subtitle": "구성 프로젝트 개요",
    "dashboard.loading": "대시보드 불러오는 중...",
    "dashboard.loadError": "대시보드 데이터를 불러오지 못했습니다",
    "dashboard.stat.total": "전체 프로젝트",
    "dashboard.stat.drafts": "초안",
    "dashboard.stat.generated": "생성 완료",
    "dashboard.stat.templates": "템플릿",
    "dashboard.recent": "최근 프로젝트",
    "dashboard.col.name": "이름",
    "dashboard.col.platform": "플랫폼",
    "dashboard.col.hostname": "호스트명",
    "dashboard.col.status": "상태",
    "dashboard.col.updated": "수정일",
    "dashboard.empty": "아직 프로젝트가 없습니다. 첫 구성을 만들어 보세요.",
    "dashboard.unnamed": "이름 없음",
    "dashboard.import.success": "\"{name}\" 가져옴",
    "dashboard.import.fail": "가져오기 실패: {detail}",

    // 템플릿 라이브러리
    "templates.title": "템플릿 라이브러리",
    "templates.subtitle": "플랫폼별 재사용 구성 템플릿",
    "templates.allPlatforms": "전체 플랫폼",
    "templates.loading": "템플릿 불러오는 중...",
    "templates.empty": "템플릿이 없습니다.",
    "templates.emptyHint": "템플릿은 첫 실행 시 자동 생성됩니다. 새로고침해 보세요.",
    "templates.loadError": "템플릿을 불러오지 못했습니다",
    "templates.duplicated": "템플릿을 복제했습니다",
    "templates.duplicateFail": "복제 실패: {detail}",
    "templates.locked": "템플릿을 잠갔습니다",
    "templates.unlocked": "템플릿 잠금을 해제했습니다",
    "templates.lockFail": "잠금 변경 실패",
    "templates.confirmDelete": "템플릿 \"{name}\"을(를) 삭제할까요?",
    "templates.deleted": "템플릿을 삭제했습니다",
    "templates.deleteFail": "삭제 실패: {detail}",
    "templates.created": "템플릿에서 프로젝트를 만들었습니다",
    "templates.createFail": "템플릿에서 프로젝트 생성 실패",

    // 프로젝트 상세
    "pd.loading": "프로젝트 불러오는 중...",
    "pd.notFound": "프로젝트를 찾을 수 없습니다.",
    "pd.loadError": "프로젝트를 불러오지 못했습니다",
    "pd.unnamed": "이름 없는 프로젝트",
    "pd.validate": "검증",
    "pd.generate": "생성",
    "pd.validation.errwarn": "검증: 오류 {errors}건, 경고 {warnings}건",
    "pd.validation.warnOnly": "경고 {warnings}건으로 검증 통과",
    "pd.validation.passed": "검증 통과. 생성할 준비가 되었습니다.",
    "pd.validation.fail": "검증 실패: {detail}",
    "pd.generate.success": "구성을 생성했습니다",
    "pd.generate.fail": "생성 실패: {detail}",
    "pd.export.success": "{format} 형식으로 내보냈습니다",
    "pd.export.fail": "내보내기 실패: {detail}",
    "pd.confirmDelete": "이 프로젝트를 삭제할까요? 되돌릴 수 없습니다.",
    "pd.deleted": "프로젝트를 삭제했습니다",
    "pd.deleteFail": "삭제 실패",
    "pd.copied": "클립보드에 복사했습니다",
    "pd.copyFail": "복사 실패 — 텍스트를 직접 선택해 복사하세요",
    "pd.tab.clean": "클린 구성",
    "pd.tab.annotated": "주석 포함",
    "pd.tab.validation": "검증",
    "pd.tab.checklist": "체크리스트",
    "pd.tab.revisions": "리비전",
    "pd.tab.export": "내보내기",
    "pd.empty.clean": "아직 생성된 구성이 없습니다. 'Generate'를 눌러 구성을 만드세요.",
    "pd.empty.annotated": "주석 포함 구성이 없습니다. 먼저 구성을 생성하세요.",
    "pd.empty.validation": "검증 결과가 없습니다. 'Validate'를 눌러 구성을 확인하세요.",
    "pd.empty.checklist": "체크리스트가 없습니다. 먼저 구성을 생성하세요.",
    "pd.errCount": "오류 {n}건",
    "pd.warnCount": "경고 {n}건",
    "pd.infoCount": "정보 {n}건",
    "pd.export.title": "프로젝트 내보내기",
    "pd.export.txtLabel": "클린 구성 (TXT)",
    "pd.export.txtDesc": "CLI 명령만, 붙여넣기용",
    "pd.export.jsonLabel": "프로젝트 (JSON)",
    "pd.export.jsonDesc": "모든 설정을 포함한 전체 프로젝트 데이터",
    "pd.export.yamlLabel": "프로젝트 (YAML)",
    "pd.export.yamlDesc": "YAML 형식의 전체 프로젝트 데이터",
    "pd.export.future": "DOCX·PDF 내보내기는 향후 버전에서 지원될 예정입니다.",
    "pd.rev.count": "리비전 {n}개",
    "pd.rev.empty": "아직 리비전이 없습니다. 이 프로젝트의 변경 내역이 여기에 기록됩니다.",
    "pd.rev.unnamedSnap": "이름 없는 스냅샷",
    "pd.rev.comparing": "비교 —",
    "pd.rev.revisionAt": "리비전 {time}",
    "pd.rev.current": "현재",
    "pd.rev.selectHint": "왼쪽에서 리비전을 선택하면 변경 내역이 표시됩니다.",
    "pd.rev.added": "+{n} 추가",
    "pd.rev.removed": "-{n} 삭제",
    "pd.rev.changed": "~{n} 변경",
    "pd.rev.noSelected": "선택된 리비전이 없습니다.",
    "pd.rev.noDiff": "이 리비전과 현재 프로젝트 간 차이가 없습니다.",
    "pd.diff.op": "구분",
    "pd.diff.field": "필드",
    "pd.diff.prev": "이전",
    "pd.diff.current": "현재",
  },
};

function interpolate(str, vars) {
  if (!vars) return str;
  return str.replace(/\{(\w+)\}/g, (m, k) => (vars[k] !== undefined ? String(vars[k]) : m));
}

const I18nContext = createContext({
  lang: DEFAULT_LANG,
  setLang: () => {},
  t: (k) => k,
});

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved === "ko" || saved === "en" ? saved : DEFAULT_LANG;
    } catch {
      return DEFAULT_LANG;
    }
  });

  const setLang = useCallback((l) => {
    const next = l === "ko" ? "ko" : "en";
    setLangState(next);
    try { localStorage.setItem(STORAGE_KEY, next); } catch { /* ignore */ }
  }, []);

  const t = useCallback((key, vars) => {
    const table = DICT[lang] || DICT.en;
    let s = table[key];
    if (s === undefined) s = DICT.en[key];
    if (s === undefined) s = key;
    return interpolate(s, vars);
  }, [lang]);

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
