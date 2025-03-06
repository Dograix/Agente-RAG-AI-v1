import { createTheme } from '@mui/material/styles';
import { ptBR } from '@mui/material/locale';
import { UI_CONFIG } from './config';

export const theme = createTheme(
    {
        palette: {
            primary: {
                main: UI_CONFIG.colors.primary.main,
            },
            secondary: {
                main: UI_CONFIG.colors.secondary.main,
            },
            success: {
                main: UI_CONFIG.colors.success.main,
            },
            error: {
                main: UI_CONFIG.colors.error.main,
            },
            warning: {
                main: UI_CONFIG.colors.warning.main,
            },
            info: {
                main: UI_CONFIG.colors.info.main,
            },
            background: {
                default: UI_CONFIG.colors.background.default,
            },
            text: {
                primary: UI_CONFIG.colors.text.primary,
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