import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiService } from '../services/api';
import { UI_CONFIG } from '../config';

export interface Document {
    id: string;
    filename: string;
    file_type: string;
    upload_date: string;
    status: string;
    size_bytes: number;
    processed: boolean;
    embedding_count?: number;
    error_message?: string;
}

export const useDocument = () => {
    const queryClient = useQueryClient();

    // Lista todos os documentos
    const useDocuments = () => {
        return useQuery(
            'documents',
            () => apiService.listDocuments(),
            {
                staleTime: 5000,
            }
        );
    };

    // Upload de documento
    const useUploadDocument = () => {
        return useMutation(
            async (file: File) => {
                // Validação do tamanho do arquivo
                if (file.size > UI_CONFIG.DOCUMENTS.MAX_FILE_SIZE) {
                    throw new Error('FILE_TOO_LARGE');
                }

                // Validação do tipo do arquivo
                if (!UI_CONFIG.DOCUMENTS.ALLOWED_FILE_TYPES.includes(file.type)) {
                    throw new Error('INVALID_FILE_TYPE');
                }

                return apiService.uploadDocument(file);
            },
            {
                onSuccess: () => {
                    queryClient.invalidateQueries('documents');
                },
            }
        );
    };

    // Deleta um documento
    const useDeleteDocument = () => {
        return useMutation(
            (id: string) => apiService.deleteDocument(id),
            {
                onSuccess: () => {
                    queryClient.invalidateQueries('documents');
                },
            }
        );
    };

    // Monitora o status de processamento de um documento
    const useDocumentStatus = (documentId: string) => {
        return useQuery(
            ['document-status', documentId],
            () => apiService.getDocumentStatus(documentId),
            {
                enabled: !!documentId,
                refetchInterval: (data) => {
                    // Continua atualizando até o documento ser processado ou falhar
                    if (data?.data?.status === 'processing') {
                        return 2000; // Atualiza a cada 2 segundos
                    }
                    return false; // Para de atualizar
                },
            }
        );
    };

    // Formata o tamanho do arquivo
    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
    };

    // Verifica se um arquivo é válido
    const isValidFile = (file: File): boolean => {
        return (
            file.size <= UI_CONFIG.DOCUMENTS.MAX_FILE_SIZE &&
            UI_CONFIG.DOCUMENTS.ALLOWED_FILE_TYPES.includes(file.type)
        );
    };

    return {
        useDocuments,
        useUploadDocument,
        useDeleteDocument,
        useDocumentStatus,
        formatFileSize,
        isValidFile,
    };
};

export default useDocument; 