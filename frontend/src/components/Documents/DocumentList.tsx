import React, { useState } from 'react';
import {
    Box,
    Paper,
    Typography,
    Button,
    List,
    ListItem,
    ListItemText,
    ListItemSecondary,
    IconButton,
    Chip,
    CircularProgress,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
} from '@mui/material';
import {
    Delete as DeleteIcon,
    CloudDownload as DownloadIcon,
    Add as AddIcon,
} from '@mui/icons-material';
import { useDocument } from '../../hooks/useDocument';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import FileUploadDialog from './FileUploadDialog';

const DocumentList: React.FC = () => {
    const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

    const {
        useDocuments,
        useDeleteDocument,
        formatFileSize,
    } = useDocument();

    const { data: documents, isLoading } = useDocuments();
    const { mutate: deleteDocument, isLoading: isDeleting } = useDeleteDocument();

    const handleDeleteClick = (documentId: string) => {
        setSelectedDocument(documentId);
        setDeleteDialogOpen(true);
    };

    const handleConfirmDelete = async () => {
        if (selectedDocument) {
            try {
                await deleteDocument(selectedDocument);
                setDeleteDialogOpen(false);
                setSelectedDocument(null);
            } catch (error) {
                console.error('Erro ao deletar documento:', error);
            }
        }
    };

    const getStatusColor = (status: string): string => {
        switch (status.toLowerCase()) {
            case 'processed':
                return 'success';
            case 'processing':
                return 'warning';
            case 'error':
                return 'error';
            default:
                return 'default';
        }
    };

    if (isLoading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 3,
                }}
            >
                <Typography variant="h5">Documentos</Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setIsUploadDialogOpen(true)}
                >
                    Adicionar Documento
                </Button>
            </Box>

            <Paper elevation={2} sx={{ borderRadius: 2 }}>
                <List>
                    {documents?.data.map((doc: any) => (
                        <ListItem
                            key={doc.id}
                            divider
                            secondaryAction={
                                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                    <Chip
                                        label={doc.status}
                                        color={getStatusColor(doc.status)}
                                        size="small"
                                    />
                                    <IconButton
                                        edge="end"
                                        aria-label="download"
                                        onClick={() => {/* Implementar download */}}
                                    >
                                        <DownloadIcon />
                                    </IconButton>
                                    <IconButton
                                        edge="end"
                                        aria-label="delete"
                                        onClick={() => handleDeleteClick(doc.id)}
                                        disabled={isDeleting}
                                    >
                                        <DeleteIcon />
                                    </IconButton>
                                </Box>
                            }
                        >
                            <ListItemText
                                primary={doc.filename}
                                secondary={
                                    <>
                                        {`Tipo: ${doc.file_type.toUpperCase()} • Tamanho: ${formatFileSize(
                                            doc.size_bytes
                                        )}`}
                                        <br />
                                        {`Upload em: ${format(
                                            new Date(doc.upload_date),
                                            "dd 'de' MMMM 'às' HH:mm",
                                            { locale: ptBR }
                                        )}`}
                                    </>
                                }
                            />
                        </ListItem>
                    ))}
                    {documents?.data.length === 0 && (
                        <ListItem>
                            <ListItemText
                                primary="Nenhum documento encontrado"
                                secondary="Clique em 'Adicionar Documento' para começar"
                            />
                        </ListItem>
                    )}
                </List>
            </Paper>

            {/* Diálogo de Upload */}
            <FileUploadDialog
                open={isUploadDialogOpen}
                onClose={() => setIsUploadDialogOpen(false)}
            />

            {/* Diálogo de Confirmação de Deleção */}
            <Dialog
                open={deleteDialogOpen}
                onClose={() => setDeleteDialogOpen(false)}
            >
                <DialogTitle>Confirmar Exclusão</DialogTitle>
                <DialogContent>
                    <Typography>
                        Tem certeza que deseja excluir este documento?
                        Esta ação não pode ser desfeita.
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button
                        onClick={() => setDeleteDialogOpen(false)}
                        disabled={isDeleting}
                    >
                        Cancelar
                    </Button>
                    <Button
                        onClick={handleConfirmDelete}
                        color="error"
                        disabled={isDeleting}
                    >
                        {isDeleting ? 'Excluindo...' : 'Excluir'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default DocumentList; 