import { createTheme } from '@mui/material/styles';
import { ptBR } from '@mui/material/locale';
import { UI_CONFIG } from './config';

export const theme = createTheme(
    {
        palette: {
            primary: {
                main: UI_CONFIG.THEME.PRIMARY_COLOR,
            },
            secondary: {
                main: UI_CONFIG.THEME.SECONDARY_COLOR,
            },
            success: {
                main: UI_CONFIG.THEME.SUCCESS_COLOR,
            },
            error: {
                main: UI_CONFIG.THEME.ERROR_COLOR,
            },
            warning: {
                main: UI_CONFIG.THEME.WARNING_COLOR,
            },
            info: {
                main: UI_CONFIG.THEME.INFO_COLOR,
            },
            background: {
                default: UI_CONFIG.THEME.BACKGROUND_COLOR,
            },
            text: {
                primary: UI_CONFIG.THEME.TEXT_COLOR,
            },
        },
        typography: {
            fontFamily: [
                'Inter',
                'Roboto',
                '"Helvetica Neue"',
                'Arial',
                'sans-serif',
            ].join(','),
            h1: {
                fontWeight: 700,
            },
            h2: {
                fontWeight: 600,
            },
            h3: {
                fontWeight: 600,
            },
            h4: {
                fontWeight: 600,
            },
            h5: {
                fontWeight: 600,
            },
            h6: {
                fontWeight: 600,
            },
        },
        shape: {
            borderRadius: 8,
        },
        components: {
            MuiButton: {
                styleOverrides: {
                    root: {
                        textTransform: 'none',
                        fontWeight: 600,
                    },
                },
            },
            MuiPaper: {
                styleOverrides: {
                    root: {
                        backgroundImage: 'none',
                    },
                },
            },
            MuiAppBar: {
                styleOverrides: {
                    root: {
                        backgroundImage: 'none',
                    },
                },
            },
            MuiDrawer: {
                styleOverrides: {
                    paper: {
                        backgroundImage: 'none',
                    },
                },
            },
            MuiDialog: {
                styleOverrides: {
                    paper: {
                        borderRadius: 12,
                    },
                },
            },
            MuiCard: {
                styleOverrides: {
                    root: {
                        borderRadius: 12,
                    },
                },
            },
            MuiListItem: {
                styleOverrides: {
                    root: {
                        borderRadius: 8,
                    },
                },
            },
            MuiChip: {
                styleOverrides: {
                    root: {
                        borderRadius: 6,
                    },
                },
            },
        },
    },
    ptBR
); 